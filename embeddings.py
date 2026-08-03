"""
Foundry RAG Assistant - Embeddings Module
Foundry Local SDK ile embedding oluşturma ve yönetimi.
Resmi API: model.get_embedding_client() -> client.generate_embedding() / client.generate_embeddings()
"""

import logging
import math
from typing import List, Optional, Any
from foundry_local_sdk import Configuration, FoundryLocalManager
from config import CONFIG

logger = logging.getLogger(__name__)


def select_device_variant(model, device: str) -> None:
    """Modelin istenen cihaz varyantini sec.

    device "auto" ise veya belirtilmediyse, oncelikle GPU (cuda/directml/gpu) varyantini arayip secer;
    GPU varyanti yoksa varsayilanda birakir.
    device "cuda-gpu", "generic-cpu" gibi spesifik ise id'sinde bu ifade gecen varyanti secer.
    """
    if not hasattr(model, "variants") or not model.variants:
        logger.warning(f"Model varyantlari bulunamadi ({getattr(model, 'alias', 'unknown')})")
        return

    if device and device != "auto":
        for variant in model.variants:
            if device in variant.id:
                model.select_variant(variant)
                logger.info(f"Spesifik model varyanti secildi ({model.alias}): {variant.id}")
                return
        logger.warning(
            f"'{device}' varyanti bulunamadi ({model.alias}), "
            f"otomatik GPU aramasina geciliyor..."
        )

    # "auto" veya spesifik varyant bulunamadiysa: GPU varyantlarini ara (cuda, directml, gpu)
    gpu_keywords = ["cuda", "directml", "gpu"]
    for keyword in gpu_keywords:
        for variant in model.variants:
            if keyword in variant.id.lower():
                model.select_variant(variant)
                logger.info(f"Otomatik GPU varyanti secildi ({model.alias}): {variant.id}")
                return

    model_id = getattr(model, "id", "unknown")
    logger.info(
        f"GPU varyanti bulunamadi/secilemedi ({model.alias}), "
        f"varsayilan varyant kullaniliyor: {model_id}"
    )


class EmbeddingManager:
    """Foundry Local embedding model yöneticisi."""

    def __init__(self):
        self.model_alias = CONFIG.embedding_model_alias
        self._model = None
        self._client = None
        self._manager = None
        self._initialized = False

    def initialize(self):
        """SDK'yi başlat ve modeli yükle."""
        if self._initialized:
            return

        logger.info("Foundry Local SDK baslatiliyor...")

        config = Configuration(
            app_name=CONFIG.app_name,
            log_level=CONFIG.log_level
        )

        if CONFIG.model_cache_dir:
            config.model_cache_dir = CONFIG.model_cache_dir

        if not getattr(FoundryLocalManager, "instance", None):
            FoundryLocalManager.initialize(config)
        self._manager = FoundryLocalManager.instance

        # EP'leri indir ve kaydet (Windows icin)
        logger.info("Execution Provider'lar kontrol ediliyor...")
        self._manager.download_and_register_eps(
            progress_callback=lambda ep, p: logger.info(f"  {ep}: {p:.1f}%")
        )

        # Modeli al
        logger.info(f"Embedding modeli yukleniyor: {self.model_alias}")
        self._model = self._manager.catalog.get_model(self.model_alias)
        select_device_variant(self._model, CONFIG.embedding_device)

        # Indir (sadece onbellekte yoksa)
        if not self._model.is_cached:
            self._model.download(
                progress_callback=lambda p: logger.info(f"  Indiriliyor: {p:.1f}%")
            )
        else:
            logger.info(f"  Model zaten var, indirme atlandi")

        # Yükle
        self._model.load()
        self._client = self._model.get_embedding_client()

        self._initialized = True
        logger.info(f"Embedding modeli hazir: {self.model_alias}")

    def embed_text(self, text: str) -> List[float]:
        """Tek bir metni embedding'e cevir.

        API: client.generate_embedding(text) -> response.data[0].embedding
        """
        if not self._initialized:
            self.initialize()

        response = self._client.generate_embedding(text)
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Birden fazla metni toplu embedding'e cevir."""
        if not self._initialized:
            self.initialize()

        if not texts:
            return []

        return [self.embed_text(t) for t in texts]

    def shutdown(self):
        """Modeli bellekten kaldir."""
        if self._model:
            self._model.unload()
            self._initialized = False
            logger.info("Embedding modeli kaldirildi")

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Iki vektor arasindaki kosinus benzerligini hesapla.

    Sonuc [-1, 1] araliginda. 1 = tamamen ayni, 0 = iliskisiz.
    """
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def vectorized_find_top_k(
    query_embedding: List[float],
    candidates: List[dict],
    k: int = 5,
    embeddings_matrix: Optional[Any] = None
) -> List[dict]:
    """NumPy matris matris çarpımı ile en yüksek benzerlikteki k parçayı bul.

    Args:
        query_embedding: Sorgu vektörü
        candidates: Candidate metadata dict listesi
        k: Döndürülecek en iyi sonuç sayısı
        embeddings_matrix: Opsiyonel 2D Float32 NumPy matrisi

    Returns:
        Similarities hesaplanmış ve sıralanmış candidate listesi
    """
    import numpy as np

    if not candidates:
        return []

    q_vec = np.asarray(query_embedding, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []
    q_vec = q_vec / q_norm

    if embeddings_matrix is None:
        raw_matrix = np.array([c["embedding"] for c in candidates], dtype=np.float32)
    else:
        raw_matrix = embeddings_matrix

    norms = np.linalg.norm(raw_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_matrix = raw_matrix / norms

    sims = np.dot(norm_matrix, q_vec)

    top_indices = np.argsort(sims)[::-1][:k]

    results = []
    for idx in top_indices:
        cand = dict(candidates[idx])
        cand["similarity"] = float(sims[idx])
        results.append(cand)

    return results


def find_top_k(query_embedding: List[float], 
               candidates: List[dict], 
               k: int = 5) -> List[dict]:
    """En benzer k adet parcayi bul."""
    return vectorized_find_top_k(query_embedding, candidates, k=k)

