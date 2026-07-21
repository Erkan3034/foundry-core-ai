"""
Foundry RAG Assistant - Database Module
SQLite veritabanı işlemleri: belge parçaları, embedding vektörleri, metadata.
"""

import sqlite3
import json
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import List, Optional, Tuple, Any
import numpy as np
from config import CONFIG
from search_text import normalize_tr, build_fts_query

logger = logging.getLogger(__name__)


def pack_embedding(embedding: Optional[List[float]]) -> Optional[bytes]:
    """List[float] embedding'ini Float32 binary bytes (BLOB) olarak paketle."""
    if embedding is None or len(embedding) == 0:
        return None
    return np.array(embedding, dtype=np.float32).tobytes()


def unpack_embedding(blob: Optional[bytes]) -> Optional[np.ndarray]:
    """Float32 binary bytes (BLOB) verisini NumPy np.ndarray'e geri aç."""
    if blob is None or len(blob) == 0:
        return None
    return np.frombuffer(blob, dtype=np.float32)


class Database:
    """SQLite veritabanı yöneticisi. Singleton pattern."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db_path = CONFIG.db_path
        self._init_database()

    def _init_database(self):
        """Veritabanı şemasını oluştur."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Belgeler tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Parçalar tablosu (chunking sonucu)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding TEXT,  -- JSON array olarak saklanır
                    embedding_blob BLOB, -- Float32 binary array
                    token_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                    UNIQUE(document_id, chunk_index)
                )
            """)

            # Migration: Var olan veritabanları için embedding_blob sütununu kontrol et ve ekle
            try:
                cursor.execute("ALTER TABLE chunks ADD COLUMN embedding_blob BLOB")
            except sqlite3.OperationalError:
                pass  # Sütun zaten var

            # Metadata tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # İndeksler
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(document_id)
            """)

            # Anahtar kelime (BM25) indeksi - hibrit arama icin.
            # rowid = chunks.id olacak sekilde elle senkron tutulur.
            # Icerik NORMALIZE edilmis metindir (Turkce diakritikler katlanmis),
            # cunku korpus 'GUVENLIGI', kullanici 'güvenliği' yazar.
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text_norm)
            """)

            conn.commit()
            logger.info(f"Veritabanı hazır: {self.db_path}")

    @contextmanager
    def _get_connection(self):
        """Bağlantı context manager'ı (WAL modu ve timeout ile eşzamanlı erişim koruması)."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
            yield conn
        finally:
            conn.close()

    def add_document(self, source: str, file_path: str, content: str) -> int:
        """Belge ekle. Dönen değer: document_id"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO documents (source, file_path, content) VALUES (?, ?, ?)",
                (source, file_path, content)
            )
            conn.commit()
            doc_id = cursor.lastrowid
            logger.info(f"Belge eklendi: {source} (ID: {doc_id})")
            return doc_id

    def add_chunk(self, document_id: int, chunk_index: int, 
                  chunk_text: str, embedding: Optional[List[float]] = None,
                  token_count: Optional[int] = None) -> int:
        """Parça ekle (Float32 BLOB olarak kaydeder).

        NOT: embedding JSON sütunu artık YAZILMAZ. 1024 float'ın JSON'u ~20KB,
        BLOB'u 4KB; ikisini birden yazmak 5 kat yer israfıydı. Sütun sadece
        migration görmemiş eski kayıtları okuyabilmek için şemada duruyor.
        """
        embedding_blob = pack_embedding(embedding)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO chunks
                   (document_id, chunk_index, chunk_text, embedding, embedding_blob, token_count)
                   VALUES (?, ?, ?, NULL, ?, ?)""",
                (document_id, chunk_index, chunk_text, embedding_blob, token_count)
            )
            chunk_id = cursor.lastrowid
            # FTS indeksini AYNI transaction icinde guncelle ki senkron kaymasin
            cursor.execute(
                "INSERT INTO chunks_fts (rowid, text_norm) VALUES (?, ?)",
                (chunk_id, normalize_tr(chunk_text))
            )
            conn.commit()
            return chunk_id

    def add_chunks_bulk(self, document_id: int, chunks: List[dict]) -> List[int]:
        """Birden fazla parcayi TEK transaction ile ekle.

        add_chunk her cagrida yeni baglanti acip commit eder; N parca icin
        N baglanti ve N fsync demektir. Buyuk belgelerde yuklemeyi kilitleyen
        darbogaz budur. Burada tek baglanti + executemany kullanilir.

        chunks: [{'chunk_index', 'chunk_text', 'embedding', 'token_count'}, ...]
        Donen: eklenen satirlarin id listesi (chunks ile ayni sirada).

        Hata durumunda commit edilmez, baglanti kapanirken transaction geri
        alinir; yarim veri kalmaz.
        """
        if not chunks:
            return []

        rows = [
            (
                document_id,
                c["chunk_index"],
                c["chunk_text"],
                pack_embedding(c.get("embedding")),
                c.get("token_count"),
            )
            for c in chunks
        ]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """INSERT INTO chunks
                   (document_id, chunk_index, chunk_text, embedding, embedding_blob, token_count)
                   VALUES (?, ?, ?, NULL, ?, ?)""",
                rows
            )
            # DIKKAT: executemany() sonrasi cursor.lastrowid None dondurur.
            # SQLite'in kendi last_insert_rowid() fonksiyonu ayni baglantida guvenilir.
            last_id = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]

            # executemany tek tek id vermez; ardisik atandiklari icin geriye dogru turet
            first_id = last_id - len(rows) + 1
            ids = list(range(first_id, last_id + 1))

            # FTS indeksini AYNI transaction icinde doldur
            cursor.executemany(
                "INSERT INTO chunks_fts (rowid, text_norm) VALUES (?, ?)",
                [(cid, normalize_tr(c["chunk_text"]))
                 for cid, c in zip(ids, chunks)]
            )
            conn.commit()
        logger.info(f"{len(ids)} parca tek transaction ile eklendi (belge {document_id})")
        return ids

    def migrate_drop_json_embeddings(self, vacuum: bool = False) -> int:
        """Eski kayıtlardaki gereksiz JSON embedding'leri temizle.

        Sadece embedding_blob'u DOLU olan satırların JSON'u silinir; BLOB'u
        olmayan satırda JSON tek veri kaynağıdır ve korunur.

        vacuum=True ise VACUUM ile disk alanı fiilen geri kazanılır
        (SQLite silinen sayfaları kendiliğinden iade etmez).

        Dönen: temizlenen satır sayısı.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chunks SET embedding = NULL "
                "WHERE embedding IS NOT NULL AND embedding_blob IS NOT NULL"
            )
            cleared = cursor.rowcount
            conn.commit()

            if vacuum and cleared:
                conn.execute("VACUUM")

        if cleared:
            logger.info(f"{cleared} satirda gereksiz JSON embedding temizlendi")
        return cleared

    def get_all_chunks_vector_data(self) -> Tuple[List[dict], Optional[np.ndarray]]:
        """Tüm parçaların metadata listesini ve hizalanmış NumPy 2D vektör matrisini döndürür."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.document_id, c.chunk_index, c.chunk_text, 
                       c.embedding, c.embedding_blob, d.source, d.file_path
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE c.embedding_blob IS NOT NULL OR c.embedding IS NOT NULL
            """)
            rows = cursor.fetchall()

            candidates = []
            vectors = []

            for row in rows:
                vec = None
                if row["embedding_blob"]:
                    vec = unpack_embedding(row["embedding_blob"])
                elif row["embedding"]:
                    vec = np.array(json.loads(row["embedding"]), dtype=np.float32)

                if vec is not None:
                    candidates.append({
                        "id": row["id"],
                        "document_id": row["document_id"],
                        "chunk_index": row["chunk_index"],
                        "chunk_text": row["chunk_text"],
                        "embedding": vec,
                        "source": row["source"],
                        "file_path": row["file_path"]
                    })
                    vectors.append(vec)

            if not vectors:
                return [], None

            embeddings_matrix = np.vstack(vectors)
            return candidates, embeddings_matrix

    def search_keyword(self, query: str, limit: int = 10) -> List[dict]:
        """BM25 anahtar kelime araması (hibrit aramanın seyrek/sparse ayağı).

        Dense embedding Türkçe morfolojisinde zayıflar ("izin" sorgusu
        "izinleri" geçen parçayı kaçırabilir); BM25 kök/ön-ek eşleşmesiyle
        bunu telafi eder.

        Dönen: [{'id', 'chunk_text', 'source', 'file_path', 'bm25_score'}, ...]
        en alakalıdan başlayarak. Eşleşme yoksa boş liste.
        """
        match_expr = build_fts_query(query)
        if not match_expr:
            return []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """SELECT c.id, c.chunk_text, d.source, d.file_path,
                              bm25(chunks_fts) AS score
                       FROM chunks_fts f
                       JOIN chunks c ON c.id = f.rowid
                       JOIN documents d ON d.id = c.document_id
                       WHERE chunks_fts MATCH ?
                       ORDER BY score
                       LIMIT ?""",
                    (match_expr, limit)
                )
            except sqlite3.OperationalError as e:
                # Bozuk MATCH ifadesi tüm sorguyu düşürmemeli; dense ayak yeter
                logger.warning(f"FTS sorgusu basarisiz ({e}); anahtar kelime ayagi atlandi")
                return []

            # bm25() daha alakalı için daha NEGATİF döner; işareti çevirip
            # "büyük = daha iyi" hâline getir.
            return [
                {
                    "id": row["id"],
                    "chunk_text": row["chunk_text"],
                    "source": row["source"],
                    "file_path": row["file_path"],
                    "bm25_score": -row["score"],
                }
                for row in cursor.fetchall()
            ]

    def rebuild_fts_index(self) -> int:
        """FTS indeksini chunks tablosundan sıfırdan kur.

        Mevcut veritabanları FTS tablosu eklenmeden önce doldurulmuştu;
        bir kez çalıştırılması gerekir. Idempotenttir.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks_fts")
            cursor.execute("SELECT id, chunk_text FROM chunks")
            rows = cursor.fetchall()
            cursor.executemany(
                "INSERT INTO chunks_fts (rowid, text_norm) VALUES (?, ?)",
                [(r["id"], normalize_tr(r["chunk_text"])) for r in rows]
            )
            conn.commit()
        logger.info(f"FTS indeksi yeniden kuruldu: {len(rows)} parca")
        return len(rows)

    def get_all_chunks_with_embeddings(self) -> List[dict]:
        """Geriye dönük uyumluluk için eski metot."""
        candidates, _ = self.get_all_chunks_vector_data()
        return candidates

    def get_document_chunks(self, document_id: int) -> List[dict]:
        """Belirli bir belgenin tüm parçalarını getir."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index",
                (document_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def is_file_ingested(self, file_path: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents WHERE file_path = ?", (file_path,))
            return cursor.fetchone()[0] > 0

    def delete_document(self, document_id: int) -> bool:
        """Belge ve parçalarını sil."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # FTS satırlarını ÖNCE sil: chunks silindikten sonra hangi rowid'lerin
            # bu belgeye ait olduğunu öğrenemeyiz (yetim FTS kaydı kalır).
            cursor.execute(
                "DELETE FROM chunks_fts WHERE rowid IN "
                "(SELECT id FROM chunks WHERE document_id = ?)",
                (document_id,)
            )
            cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Belge silindi: ID {document_id}")
                try:
                    from retriever import Retriever
                    Retriever.invalidate_cache()
                except Exception:
                    pass
            return deleted

    def list_documents(self) -> List[dict]:
        """Tüm belgeleri listele."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.*, COUNT(c.id) as chunk_count 
                FROM documents d
                LEFT JOIN chunks c ON d.id = c.document_id
                GROUP BY d.id
                ORDER BY d.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> dict:
        """Veritabanı istatistikleri."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as doc_count FROM documents")
            doc_count = cursor.fetchone()["doc_count"]

            cursor.execute("SELECT COUNT(*) as chunk_count FROM chunks")
            chunk_count = cursor.fetchone()["chunk_count"]

            cursor.execute("SELECT COUNT(*) as embedded_count FROM chunks WHERE embedding IS NOT NULL OR embedding_blob IS NOT NULL")
            embedded_count = cursor.fetchone()["embedded_count"]

            return {
                "documents": doc_count,
                "chunks": chunk_count,
                "embedded_chunks": embedded_count
            }

    def clear_all(self):
        """Tüm verileri temizle. DİKKAT!"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks_fts")
            cursor.execute("DELETE FROM chunks")
            cursor.execute("DELETE FROM documents")
            conn.commit()
            logger.warning("Tüm veriler silindi!")
            try:
                from retriever import Retriever
                Retriever.invalidate_cache()
            except Exception:
                pass


# Singleton instance
db = Database()
