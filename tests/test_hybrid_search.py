"""
Foundry RAG Assistant - Hibrit Arama Testleri (Adim 4)

Dense (embedding) arama Turkce morfolojisinde zayiflar: "izin" sorgusu
"izinler/izinleri/izinden" gecen parcayi kacirabilir. BM25 (SQLite FTS5)
kok/on-ek eslesmesiyle bunu telafi eder.

Iki Turkce'ye ozgu zorluk test ediliyor:
1. DIAKRITIK: korpus "GUVENLIGI" yazilmis, kullanici "güvenliği" yaziyor.
2. EKLEME: Turkce sondan eklemeli; "parola" sorgusu "parolalar"i bulmali.
"""

import pytest
import numpy as np

from database import Database
from search_text import normalize_tr, build_fts_query


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


CORPUS = [
    "Parola Kurallari. Tum kurumsal hesap parolalari en az 12 karakter olmali. "
    "Parolalar 90 gunde bir degistirilmelidir.",
    "Yillik Izin. Calisanlar ilk yilindan sonra 14 gun yillik izin hakki kazanir. "
    "Izin talepleri birim yoneticisi tarafindan onaylanir.",
    "Seyahat Politikasi. Ucak bileti ve konaklama masraflari sirket tarafindan karsilanir. "
    "Harcirah gunluk 500 TL olarak odenir.",
]


def _seed(db, dim=4):
    doc_id = db.add_document("test.txt", "/test.txt", "x")
    db.add_chunks_bulk(doc_id, [
        {"chunk_index": i, "chunk_text": text,
         "embedding": [float(i)] * dim, "token_count": 10}
        for i, text in enumerate(CORPUS)
    ])
    return doc_id


class TestTurkishNormalization:
    """Diakritik katlama: kullanici 'güvenliği' yazar, korpus 'guvenligi' icerir."""

    @pytest.mark.parametrize("giris,beklenen", [
        ("değiştirilmeli", "degistirilmeli"),
        ("GÜVENLİĞİ", "guvenligi"),
        ("Yıllık İzin", "yillik izin"),
        ("şirket çalışanı", "sirket calisani"),
        ("PAROLAMI", "parolami"),
        ("harcırah", "harcirah"),
    ])
    def test_folds_turkish_characters(self, giris, beklenen):
        assert normalize_tr(giris) == beklenen

    def test_idempotent(self):
        once = normalize_tr("Değiştirilmeli")
        assert normalize_tr(once) == once

    def test_handles_empty(self):
        assert normalize_tr("") == ""


class TestFtsQueryBuilder:
    """Turkce sondan eklemeli: 'parola' sorgusu 'parolalar'i bulmali -> prefix."""

    def test_terms_become_prefix_queries(self):
        q = build_fts_query("yillik izin")
        assert "izin*" in q

    def test_long_terms_are_truncated_for_stemming(self):
        """'parolami' tam haliyle 'parolalar'i bulamaz; kok prefix'e kisaltilir."""
        q = build_fts_query("parolami")
        assert "parol*" in q

    def test_normalizes_before_building(self):
        q = build_fts_query("Yıllık İZİN")
        assert "izin*" in q
        assert "İ" not in q

    def test_strips_fts_operators(self):
        """Kullanici girdisi FTS5 sozdizimini bozmamali (injection)."""
        q = build_fts_query('izin AND "OR" NEAR(')
        assert '"' not in q
        assert "(" not in q

    def test_empty_query_returns_empty(self):
        assert build_fts_query("") == ""
        assert build_fts_query("!!! ???") == ""


class TestKeywordSearch:

    def test_finds_exact_term(self, db):
        _seed(db)
        hits = db.search_keyword("harcirah", limit=5)
        assert len(hits) >= 1
        assert "Harcirah" in hits[0]["chunk_text"]

    def test_finds_across_turkish_suffix(self, db):
        """'parola' -> 'parolalari' gecen parcayi bulmali."""
        _seed(db)
        hits = db.search_keyword("parola", limit=5)
        assert any("Parola" in h["chunk_text"] for h in hits)

    def test_finds_despite_user_diacritics(self, db):
        """Kullanici 'İZİN' yazar, korpus 'Izin' icerir."""
        _seed(db)
        hits = db.search_keyword("yıllık izin", limit=5)
        assert any("Yillik Izin" in h["chunk_text"] for h in hits)

    def test_returns_empty_for_unrelated_query(self, db):
        _seed(db)
        assert db.search_keyword("kuantum fizigi roket", limit=5) == []

    def test_ranks_by_relevance(self, db):
        _seed(db)
        hits = db.search_keyword("izin talepleri", limit=5)
        assert "Izin" in hits[0]["chunk_text"]


class TestFtsSync:
    """FTS indeksi chunks tablosuyla senkron kalmali (Adim 1'deki dersin tekrari)."""

    def test_bulk_insert_populates_fts(self, db):
        _seed(db)
        assert len(db.search_keyword("parola", limit=10)) >= 1

    def test_add_chunk_populates_fts(self, db):
        doc_id = db.add_document("a.txt", "/a.txt", "x")
        db.add_chunk(doc_id, 0, "Kurumsal VPN baglantisi SecureConnect ile kurulur", [1.0], 5)
        hits = db.search_keyword("vpn", limit=5)
        assert len(hits) == 1

    def test_delete_document_removes_from_fts(self, db):
        doc_id = _seed(db)
        assert len(db.search_keyword("harcirah", limit=5)) >= 1
        db.delete_document(doc_id)
        assert db.search_keyword("harcirah", limit=5) == []

    def test_clear_all_empties_fts(self, db):
        _seed(db)
        db.clear_all()
        assert db.search_keyword("parola", limit=5) == []
