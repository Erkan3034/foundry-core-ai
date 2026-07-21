"""
Foundry RAG Assistant - Toplu Insert Testleri (Adim 1)

Amac: add_chunk her cagrida yeni SQLite baglantisi acip commit ediyordu.
100k chunk = 100k baglanti + 100k fsync. Toplu insert bunu tek transaction'a indirir.
"""

import pytest
import numpy as np

from config import CONFIG
from database import Database, unpack_embedding


@pytest.fixture
def db(tmp_path):
    """Her test icin izole, gecici veritabani.

    CONFIG frozen dataclass oldugu icin db_path monkeypatch'lenemiyor;
    singleton'i elle kurup db_path'i dogrudan set ediyoruz.
    """
    previous = Database._instance
    instance = Database.__new__(Database)
    instance._initialized = True
    instance.db_path = str(tmp_path / "test.db")
    instance._init_database()
    Database._instance = instance
    yield instance
    Database._instance = previous


def _make_chunks(n: int, dim: int = 8):
    """n adet (chunk_index, text, embedding, token_count) uret."""
    return [
        {
            "chunk_index": i,
            "chunk_text": f"parca {i}",
            "embedding": [float(i)] * dim,
            "token_count": i,
        }
        for i in range(n)
    ]


class TestBulkInsert:

    def test_inserts_all_rows(self, db):
        doc_id = db.add_document("a.txt", "/tmp/a.txt", "icerik")
        ids = db.add_chunks_bulk(doc_id, _make_chunks(50))

        assert len(ids) == 50
        assert db.get_stats()["chunks"] == 50

    def test_roundtrip_preserves_text_and_vector(self, db):
        doc_id = db.add_document("a.txt", "/tmp/a.txt", "icerik")
        db.add_chunks_bulk(doc_id, _make_chunks(5))

        candidates, matrix = db.get_all_chunks_vector_data()

        assert len(candidates) == 5
        assert matrix.shape == (5, 8)
        texts = sorted(c["chunk_text"] for c in candidates)
        assert texts == sorted(f"parca {i}" for i in range(5))
        # 3. parcanin vektoru [3.0]*8 olmali
        row = next(c for c in candidates if c["chunk_text"] == "parca 3")
        assert np.allclose(row["embedding"], [3.0] * 8)

    def test_uses_exactly_one_connection(self, db, monkeypatch):
        """Asil kazanc burada: N chunk icin 1 baglanti, N degil."""
        calls = {"n": 0}
        original = Database._get_connection

        def counting(self):
            calls["n"] += 1
            return original(self)

        monkeypatch.setattr(Database, "_get_connection", counting)

        doc_id = db.add_document("a.txt", "/tmp/a.txt", "icerik")
        calls["n"] = 0  # add_document'inkini sayma
        db.add_chunks_bulk(doc_id, _make_chunks(100))

        assert calls["n"] == 1, f"100 chunk icin {calls['n']} baglanti acildi"

    def test_atomic_on_failure(self, db):
        """Ortada hata olursa hicbir satir kalmamali (yarim veri yok)."""
        doc_id = db.add_document("a.txt", "/tmp/a.txt", "icerik")
        chunks = _make_chunks(10)
        chunks[7]["chunk_text"] = None  # NOT NULL ihlali

        with pytest.raises(Exception):
            db.add_chunks_bulk(doc_id, chunks)

        assert db.get_stats()["chunks"] == 0

    def test_equivalent_to_add_chunk(self, db):
        """Toplu yol ile tekil yol ayni veriyi uretmeli."""
        doc_a = db.add_document("a.txt", "/tmp/a.txt", "x")
        doc_b = db.add_document("b.txt", "/tmp/b.txt", "x")

        for c in _make_chunks(6):
            db.add_chunk(doc_a, c["chunk_index"], c["chunk_text"],
                         c["embedding"], c["token_count"])
        db.add_chunks_bulk(doc_b, _make_chunks(6))

        a = sorted(db.get_document_chunks(doc_a), key=lambda r: r["chunk_index"])
        b = sorted(db.get_document_chunks(doc_b), key=lambda r: r["chunk_index"])

        assert [r["chunk_text"] for r in a] == [r["chunk_text"] for r in b]
        assert [r["token_count"] for r in a] == [r["token_count"] for r in b]
        for ra, rb in zip(a, b):
            assert np.allclose(unpack_embedding(ra["embedding_blob"]),
                               unpack_embedding(rb["embedding_blob"]))

    def test_empty_list_is_noop(self, db):
        doc_id = db.add_document("a.txt", "/tmp/a.txt", "icerik")
        assert db.add_chunks_bulk(doc_id, []) == []
        assert db.get_stats()["chunks"] == 0
