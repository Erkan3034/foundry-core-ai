"""
Foundry RAG Assistant - Reindex Script
Tüm mevcut belge parçalarının embedding'lerini seçili embedding modeli ile yeniden oluşturur.
"""

import logging
import sys
import time
from database import db
from embeddings import EmbeddingManager
from retriever import Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("reindex")


def reindex_all_chunks(batch_size: int = 32):
    """Veritabanındaki tüm parçaları yeniden vektörleştir."""
    logger.info("Yeniden indeksleme (Reindexing) başlatılıyor...")

    chunks = db.get_all_chunks()
    if not chunks:
        logger.warning("Veritabanında yeniden indekslenecek parça bulunamadı!")
        return

    logger.info(f"Toplam {len(chunks)} adet parça yeniden vektörleştirilecek.")

    embedder = EmbeddingManager()
    embedder.initialize()

    start_time = time.time()
    updated_count = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["chunk_text"] for c in batch]

        try:
            embeddings = embedder.embed_batch(texts)
            for chunk, vec in zip(batch, embeddings):
                db.save_chunk_embedding(chunk["id"], vec)
                updated_count += 1
            logger.info(f"  İşlenen parça: {updated_count}/{len(chunks)}")
        except Exception as e:
            logger.error(f"  Toplu embedding oluşturma hatası (İndeks {i}-{i+len(batch)}): {e}", exc_info=True)

    # RAM önbelleğini temizle
    Retriever.invalidate_cache()

    elapsed = time.time() - start_time
    logger.info(f"Yeniden indeksleme tamamlandı! {updated_count} parça {elapsed:.2f} saniyede güncellendi.")


if __name__ == "__main__":
    reindex_all_chunks()
