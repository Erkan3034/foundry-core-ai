"""
Foundry RAG Assistant - Retriever Module
Sorguya gore en ilgili belge parcalarini bul.
"""

import logging
from typing import List
from database import db
from embeddings import EmbeddingManager, vectorized_find_top_k
from search_fusion import reciprocal_rank_fusion
from config import CONFIG

logger = logging.getLogger(__name__)


class Retriever:
    """Semantik arama motoru (RAM Vector Cache ile optimize edilmis)."""

    _vector_cache = None  # (candidates, embeddings_matrix)

    @classmethod
    def invalidate_cache(cls):
        """RAM önbelleğini geçersiz kıl."""
        cls._vector_cache = None
        logger.debug("Retriever RAM vector cache temizlendi")

    def __init__(self, top_k: int = None, min_similarity: float = None,
                 use_hybrid: bool = None):
        self.top_k = top_k or CONFIG.top_k_retrieval
        self.min_similarity = min_similarity if min_similarity is not None else CONFIG.min_similarity
        self.use_hybrid = CONFIG.use_hybrid_search if use_hybrid is None else use_hybrid
        self.embedding_manager = EmbeddingManager()
        self._initialized = False

    def initialize(self):
        """Embedding modelini baslat."""
        if not self._initialized:
            self.embedding_manager.initialize()
            self._initialized = True

    def _get_vector_data(self):
        """RAM önbellekten veya DB'den vektör matrisini al."""
        if Retriever._vector_cache is None:
            candidates, matrix = db.get_all_chunks_vector_data()
            Retriever._vector_cache = (candidates, matrix)
        return Retriever._vector_cache

    @staticmethod
    def _clean_query(query: str) -> str:
        import re
        cleaned = re.sub(r'[\_\#\@\$]', ' ', query)
        return ' '.join(cleaned.split())

    def retrieve(self, query: str) -> List[dict]:
        """Sorguya gore en ilgili parcalari getir."""
        self.initialize()

        cleaned_query = self._clean_query(query)

        # 1. Sorguyu embedding'e cevir
        logger.debug(f"Sorgu embedding olusturuluyor: {cleaned_query[:50]}...")
        query_embedding = self.embedding_manager.embed_text(cleaned_query)

        # 2. Önbellekten veya DB'den vektör verilerini al
        candidates, matrix = self._get_vector_data()

        if not candidates or matrix is None:
            logger.warning("Veritabaninda embedding'li parca yok!")
            return []

        logger.debug(f"{len(candidates)} parca arasindan vectorized arama yapiliyor...")

        # 3. DENSE ayak: NumPy matris carpimi ile benzerlik.
        #    Fuzyon icin top_k'dan genis bir havuz cekilir; anahtar kelime
        #    ayagi bu havuz icindeki siralamayi degistirebilsin diye.
        pool_size = max(self.top_k * CONFIG.hybrid_pool_factor, 20)
        dense_results = vectorized_find_top_k(
            query_embedding,
            candidates,
            k=pool_size,
            embeddings_matrix=matrix
        )

        if not dense_results:
            return []

        # 4. SPARSE ayak + fuzyon
        ranked = self._fuse_with_keyword_search(cleaned_query, dense_results)

        # 5. Esik: normalde min_similarity, ancak anahtar kelime eslesmesi olan
        #    parcalar icin biraz daha musamahali bir taban uygulanir.
        #    Kelime eslesmesi TEK BASINA yeterli degildir; aksi halde "izin"
        #    gecen her belge alakasiz sorulara cevap olarak donerdi.
        rescue_floor = self.min_similarity * CONFIG.keyword_rescue_ratio
        keyword_ids = self._last_keyword_ids

        filtered = [
            r for r in ranked
            if r["similarity"] >= self.min_similarity
            or (r.get("id") in keyword_ids and r["similarity"] >= rescue_floor)
        ][:self.top_k]

        logger.info(
            f"{len(filtered)}/{len(ranked)} sonuc esigi gecti "
            f"(en yuksek benzerlik: {ranked[0]['similarity']:.4f}, "
            f"esik: {self.min_similarity}, hibrit: {self.use_hybrid})"
        )

        return filtered

    _last_keyword_ids: set = frozenset()

    def _fuse_with_keyword_search(self, query: str, dense_results: List[dict]) -> List[dict]:
        """Dense siralamasini BM25 siralamasiyla RRF uzerinden birlestir.

        Skorlar farkli olceklerde oldugu icin toplanmaz; siralamalar
        birlestirilir (bkz. search_fusion).
        """
        self._last_keyword_ids = frozenset()

        if not self.use_hybrid:
            return dense_results

        keyword_hits = db.search_keyword(query, limit=len(dense_results))
        if not keyword_hits:
            logger.debug("Anahtar kelime eslesmesi yok; saf dense siralama")
            return dense_results

        self._last_keyword_ids = frozenset(h["id"] for h in keyword_hits)

        by_id = {r["id"]: r for r in dense_results}
        dense_ranking = [r["id"] for r in dense_results]
        # Dense havuzunun disinda kalan kelime eslesmelerini atla: benzerlikleri
        # havuz tabaninin altinda oldugu icin rescue esigini zaten gecemezler.
        keyword_ranking = [h["id"] for h in keyword_hits if h["id"] in by_id]

        fused = reciprocal_rank_fusion([dense_ranking, keyword_ranking])

        logger.debug(
            f"Hibrit fuzyon: {len(dense_ranking)} dense + "
            f"{len(keyword_ranking)} anahtar kelime -> {len(fused)} sonuc"
        )

        return [by_id[item_id] for item_id, _ in fused]

    def retrieve_with_context(self, query: str) -> dict:
        """Sorgu + baglam + metadata dondur.

        Returns:
            {
                'query': str,
                'results': List[dict],
                'context': str,  # LLM promptu icin birlestirilmis metin
                'sources': List[str]
            }
        """
        results = self.retrieve(query)

        if not results:
            return {
                "query": query,
                "results": [],
                "context": "",
                "sources": []
            }

        # LLM promptu icin baglam olustur (MAX_CONTEXT_LENGTH'i asma)
        context_parts = []
        sources = []
        used_results = []
        total_length = 0

        for i, result in enumerate(results):
            source = result.get("source", "Bilinmeyen")
            page_info = f" | Sayfa {result['page_number']}" if result.get("page_number") else ""
            section_info = f" | Bölüm: {result['section_title']}" if result.get("section_title") else ""
            
            # Parent-Child Retrieval: Parent chunk varsa LLM bağlamına parent metni koy
            text_for_context = result.get("parent_chunk_text") or result["chunk_text"]
            
            part = (
                f"[KAYNAK: {source}{page_info}{section_info} | PARÇA {i+1}]\n"
                f"{text_for_context}"
            )

            if used_results and total_length + len(part) > CONFIG.max_context_length:
                logger.debug(f"Baglam limiti doldu, {len(results) - i} sonuc atlandi")
                break

            context_parts.append(part)
            total_length += len(part)
            used_results.append(result)
            if source not in sources:
                sources.append(source)

        context = "\n\n---\n\n".join(context_parts)

        return {
            "query": query,
            "results": used_results,
            "context": context,
            "sources": sources
        }

    def shutdown(self):
        """Kaynaklari temizle."""
        self.embedding_manager.shutdown()
        self._initialized = False
