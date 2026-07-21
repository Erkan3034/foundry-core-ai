"""
Foundry RAG Assistant - Siralama Fuzyonu

Dense (kosinus benzerligi, 0..1) ve BM25 skorlari ayni olcekte degildir:
kosinus sinirli, BM25 sinirsiz ve korpusa baglidir. Bunlari agirlikli
toplamla birlestirmek, olceklerden biri kaydiginda sessizce bozulan bir
sistem uretir.

Reciprocal Rank Fusion (RRF) skorlari degil SIRALAMALARI birlestirir:

    score(d) = SUM over rankings  1 / (k + rank(d))

Olcek bagimsizdir, normalizasyon gerektirmez ve pratikte agirlik ayarina
gore daha saglamdir. k=60 literaturdeki standart degerdir; buyudukce
siralama farklarinin etkisi azalir.
"""

from typing import Dict, List, Sequence, Tuple, Any

RRF_K = 60


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[Any]],
    k: int = RRF_K,
) -> List[Tuple[Any, float]]:
    """Birden fazla siralanmis id listesini tek siralamada birlestir.

    rankings: her biri en alakalidan baslayan id listesi
    k: sonraki siralarin etkisini bastiran sabit

    Donen: [(id, skor), ...] skora gore azalan.
    """
    scores: Dict[Any, float] = {}

    for ranking in rankings:
        for rank, item_id in enumerate(ranking):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
