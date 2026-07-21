"""
Foundry RAG Assistant - Depolama Formati Testleri (Adim 2)

Embedding hem JSON metin hem Float32 BLOB olarak yaziliyordu.
1024 float: JSON ~20KB, BLOB 4KB -> 5 kat sisme, 100k chunk'ta ~2GB israf.
JSON sutunu artik OKUNMUYOR (get_all_chunks_vector_data once BLOB'a bakiyor),
sadece eski kayitlar icin geriye donuk uyumluluk fallback'i.

Bu testler: yeni yazimlar JSON uretmemeli, ama eski JSON-only satirlar
hala okunabilmeli.
"""

import json
import pytest
import numpy as np

from database import Database, pack_embedding


@pytest.fixture
def db(tmp_path):
    previous = Database._instance
    instance = Database.__new__(Database)
    instance._initialized = True
    instance.db_path = str(tmp_path / "test.db")
    instance._init_database()
    Database._instance = instance
    yield instance
    Database._instance = previous


def _raw_rows(db):
    with db._get_connection() as conn:
        return conn.execute(
            "SELECT chunk_text, embedding, embedding_blob FROM chunks ORDER BY id"
        ).fetchall()


class TestNoJsonDuplication:

    def test_bulk_insert_writes_blob_only(self, db):
        doc_id = db.add_document("a.txt", "/a.txt", "x")
        db.add_chunks_bulk(doc_id, [{
            "chunk_index": 0, "chunk_text": "merhaba",
            "embedding": [1.0, 2.0, 3.0], "token_count": 3,
        }])

        row = _raw_rows(db)[0]
        assert row["embedding_blob"] is not None, "BLOB yazilmali"
        assert row["embedding"] is None, "JSON sutunu artik yazilmamali (5x israf)"

    def test_add_chunk_writes_blob_only(self, db):
        doc_id = db.add_document("a.txt", "/a.txt", "x")
        db.add_chunk(doc_id, 0, "merhaba", [1.0, 2.0, 3.0], 3)

        row = _raw_rows(db)[0]
        assert row["embedding_blob"] is not None
        assert row["embedding"] is None

    def test_vectors_still_readable(self, db):
        doc_id = db.add_document("a.txt", "/a.txt", "x")
        db.add_chunks_bulk(doc_id, [
            {"chunk_index": i, "chunk_text": f"p{i}",
             "embedding": [float(i)] * 4, "token_count": 1}
            for i in range(3)
        ])

        candidates, matrix = db.get_all_chunks_vector_data()
        assert matrix.shape == (3, 4)
        assert len(candidates) == 3


class TestBackwardCompatibility:
    """Eski veritabanlarinda JSON-only satirlar olabilir; bozulmamali."""

    def test_json_only_row_still_readable(self, db):
        doc_id = db.add_document("eski.txt", "/eski.txt", "x")
        # Migration oncesi bir satiri elle simule et: sadece JSON, BLOB yok
        with db._get_connection() as conn:
            conn.execute(
                """INSERT INTO chunks
                   (document_id, chunk_index, chunk_text, embedding, embedding_blob, token_count)
                   VALUES (?, ?, ?, ?, NULL, ?)""",
                (doc_id, 0, "eski parca", json.dumps([5.0, 6.0, 7.0, 8.0]), 4)
            )
            conn.commit()

        candidates, matrix = db.get_all_chunks_vector_data()
        assert len(candidates) == 1
        assert np.allclose(matrix[0], [5.0, 6.0, 7.0, 8.0])

    def test_mixed_old_and_new_rows(self, db):
        doc_id = db.add_document("m.txt", "/m.txt", "x")
        with db._get_connection() as conn:
            conn.execute(
                """INSERT INTO chunks
                   (document_id, chunk_index, chunk_text, embedding, embedding_blob, token_count)
                   VALUES (?, ?, ?, ?, NULL, ?)""",
                (doc_id, 0, "eski", json.dumps([1.0, 1.0]), 2)
            )
            conn.commit()
        db.add_chunks_bulk(doc_id, [
            {"chunk_index": 1, "chunk_text": "yeni",
             "embedding": [2.0, 2.0], "token_count": 2}
        ])

        candidates, matrix = db.get_all_chunks_vector_data()
        assert matrix.shape == (2, 2)


class TestJsonMigration:
    """Var olan JSON verisini temizleyip yeri geri kazanan migration."""

    def test_migration_clears_json_when_blob_exists(self, db):
        doc_id = db.add_document("a.txt", "/a.txt", "x")
        # Iki satiri da JSON+BLOB dolu olarak elle yaz (migration oncesi durum)
        with db._get_connection() as conn:
            for i in range(2):
                vec = [float(i)] * 4
                conn.execute(
                    """INSERT INTO chunks
                       (document_id, chunk_index, chunk_text, embedding, embedding_blob, token_count)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (doc_id, i, f"p{i}", json.dumps(vec), pack_embedding(vec), 4)
                )
            conn.commit()

        cleared = db.migrate_drop_json_embeddings()

        assert cleared == 2
        rows = _raw_rows(db)
        assert all(r["embedding"] is None for r in rows)
        assert all(r["embedding_blob"] is not None for r in rows)

    def test_migration_preserves_json_only_rows(self, db):
        """BLOB'u olmayan satirin JSON'u SILINMEMELI - tek veri kaynagi o."""
        doc_id = db.add_document("a.txt", "/a.txt", "x")
        with db._get_connection() as conn:
            conn.execute(
                """INSERT INTO chunks
                   (document_id, chunk_index, chunk_text, embedding, embedding_blob, token_count)
                   VALUES (?, ?, ?, ?, NULL, ?)""",
                (doc_id, 0, "sadece json", json.dumps([9.0, 9.0]), 2)
            )
            conn.commit()

        db.migrate_drop_json_embeddings()

        row = _raw_rows(db)[0]
        assert row["embedding"] is not None, "BLOB yoksa JSON korunmali"
        candidates, matrix = db.get_all_chunks_vector_data()
        assert np.allclose(matrix[0], [9.0, 9.0])
