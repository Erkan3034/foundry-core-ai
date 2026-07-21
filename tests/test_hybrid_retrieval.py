"""
Foundry RAG Assistant - Hibrit Erisim Fuzyonu Testleri (Adim 4b)

Dense (kosinus) ve BM25 skorlari AYNI OLCEKTE DEGILDIR; dogrudan toplanamaz.
Bu yuzden Reciprocal Rank Fusion (RRF) kullanilir: skorlar degil SIRALAMALAR
birlestirilir.

En kritik gereksinim: "Bu konuda elimdeki belgelerde bilgi bulunmuyor."
fallback'i BOZULMAMALI. Hibrit arama alakasiz soruya kelime eslesmesiyle
sacma cevap urettirmemeli.
"""

import pytest

from search_fusion import reciprocal_rank_fusion


class TestReciprocalRankFusion:

    def test_single_ranking_preserves_order(self):
        fused = reciprocal_rank_fusion([[3, 1, 2]])
        assert [i for i, _ in fused] == [3, 1, 2]

    def test_agreement_boosts_item(self):
        """Iki listede de ust siralarda olan, tek listede birinci olani gecmeli."""
        dense = [10, 20, 30]
        keyword = [20, 30, 10]
        fused = dict(reciprocal_rank_fusion([dense, keyword]))
        # 20: 1/61 + 1/60,  10: 1/60 + 1/62
        assert fused[20] > fused[10]

    def test_item_in_one_list_only_still_included(self):
        fused = dict(reciprocal_rank_fusion([[1, 2], [99]]))
        assert 99 in fused

    def test_empty_rankings(self):
        assert reciprocal_rank_fusion([]) == []
        assert reciprocal_rank_fusion([[], []]) == []

    def test_returns_sorted_descending(self):
        fused = reciprocal_rank_fusion([[1, 2, 3], [3, 2, 1]])
        scores = [s for _, s in fused]
        assert scores == sorted(scores, reverse=True)

    def test_k_parameter_dampens_rank_influence(self):
        """Buyuk k, siralama farklarini bastirir."""
        small = dict(reciprocal_rank_fusion([[1, 2]], k=1))
        large = dict(reciprocal_rank_fusion([[1, 2]], k=1000))
        assert (small[1] - small[2]) > (large[1] - large[2])


# --------------------------------------------------------------------------
# Retriever entegrasyonu (embedding modeli mock'lanir - gercek model yuklenmez)
# --------------------------------------------------------------------------

from database import Database
from retriever import Retriever


@pytest.fixture
def db(tmp_path):
    previous = Database._instance
    instance = Database.__new__(Database)
    instance._initialized = True
    instance.db_path = str(tmp_path / "test.db")
    instance._init_database()
    Database._instance = instance
    Retriever.invalidate_cache()
    yield instance
    Database._instance = previous
    Retriever.invalidate_cache()


CORPUS = [
    ("izin_politikasi.txt",
     "Yillik izin hakki ilk yildan sonra 14 gundur. Izin talepleri yonetici onayi ister."),
    ("vpn_sss.txt",
     "VPN baglantisi SecureConnect istemcisi ile kurulur. Sifre BT tarafindan verilir."),
    ("harcirah.txt",
     "Seyahat harcirahi gunluk 500 TL olarak odenir ve masraf formu ile talep edilir."),
]


def _seed(db, vectors):
    """CORPUS'u verilen vektorlerle yukle."""
    for i, ((source, text), vec) in enumerate(zip(CORPUS, vectors)):
        doc_id = db.add_document(source, f"/{source}", text)
        db.add_chunks_bulk(doc_id, [
            {"chunk_index": 0, "chunk_text": text, "embedding": vec, "token_count": 10}
        ])


def _retriever(query_vector, **kwargs):
    """Embedding modeli mock'lanmis Retriever."""
    r = Retriever(**kwargs)
    r._initialized = True
    r.embedding_manager = type("FakeEmb", (), {
        "embed_text": staticmethod(lambda text: query_vector),
        "initialize": staticmethod(lambda: None),
    })()
    return r


class TestHybridRetrieval:

    def test_falls_back_to_dense_when_no_keyword_hit(self, db):
        """Anahtar kelime eslesmesi yoksa davranis eskisi gibi kalmali."""
        _seed(db, [[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]])
        r = _retriever([1.0, 0.0], top_k=1, min_similarity=0.5)
        results = r.retrieve("zzzz qqqq")  # hicbir terim eslesmiyor
        assert len(results) == 1
        assert "Yillik izin" in results[0]["chunk_text"]

    def test_keyword_rescues_chunk_dense_ranked_lower(self, db):
        """Dense ucuncu sirada birakiyor ama kelime eslesmesi tam -> one cikmali."""
        # Sorgu vektoru [1,0]; harcirah parcasi dense'te en dusuk
        _seed(db, [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]])
        r = _retriever([1.0, 0.0], top_k=3, min_similarity=0.0)
        results = r.retrieve("harcirah")
        sources = [x["source"] for x in results]
        assert "harcirah.txt" in sources
        assert sources.index("harcirah.txt") < 2, \
            f"kelime eslesmesi parcayi one cikarmali, siralama: {sources}"

    def test_unrelated_query_returns_empty(self, db):
        """FALLBACK KORUMASI: alakasiz soru bos donmeli."""
        _seed(db, [[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]])
        r = _retriever([0.0, 0.0, 1.0][:2], top_k=3, min_similarity=0.95)
        results = r.retrieve("kuantum fizigi roket bilimi")
        assert results == []

    def test_keyword_hit_alone_cannot_bypass_floor(self, db):
        """Kelime eslesse bile dense benzerligi tabanin altindaysa gecmemeli.

        Aksi halde 'izin' kelimesi gecen her belge, konuyla alakasiz olsa da
        cevap olarak donerdi.
        """
        _seed(db, [[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
        # Sorgu vektoru harcirah parcasina DIK (benzerlik 0)
        r = _retriever([1.0, 0.0], top_k=3, min_similarity=0.9)
        results = r.retrieve("harcirah")
        assert all(x["source"] != "harcirah.txt" for x in results), \
            "dense benzerligi cok dusukken kelime eslesmesi tek basina yeterli olmamali"

    def test_hybrid_can_be_disabled(self, db):
        """Kapatildiginda saf dense davranisina donmeli."""
        _seed(db, [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]])
        r = _retriever([1.0, 0.0], top_k=1, min_similarity=0.0, use_hybrid=False)
        results = r.retrieve("harcirah")
        assert results[0]["source"] == "izin_politikasi.txt"

    def test_results_keep_expected_shape(self, db):
        """Downstream (rag_engine) alan isimlerine guveniyor; sozlesme korunmali."""
        _seed(db, [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]])
        r = _retriever([1.0, 0.0], top_k=2, min_similarity=0.0)
        for item in r.retrieve("izin"):
            assert {"chunk_text", "similarity", "source"} <= set(item)
            assert isinstance(item["similarity"], float)
