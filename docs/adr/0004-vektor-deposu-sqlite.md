# ADR-0004: Vektor deposu olarak SQLite + NumPy brute-force + RAM onbellegi

**Durum:** Kabul edildi
**Tarih:** 2026-07-21

## Baglam

Program plani SQLite'i acikca tarif ediyor: parcalari ve embedding'leri tek bir
dosyada tut, aramada tum vektorleri belleğe al, Python'da kosinus benzerligi
hesapla, en yuksek K taneyi don. Plan bunun kucuk N icin yeterli oldugunu,
buyuk N'de ozel bir vektor veritabani gerekecegini de not ediyor.

Ilk saf uygulamada her sorguda tum vektorler diskten okunup Python dongusunde
tek tek karsilastiriliyordu. Bu iki maliyet dogurdu: disk okuma ve yorumlanan
dilde dongu.

## Karar

Depolama SQLite'ta kalir. Arama iki optimizasyonla yapilir:

1. **Vektorlestirilmis benzerlik:** Tum embedding'ler tek bir NumPy matrisinde
   tutulur; benzerlik Python dongusu yerine tek bir matris carpimiyla hesaplanir
   ([embeddings.py](../../embeddings.py) `vectorized_find_top_k`).
2. **RAM onbellegi:** Matris `Retriever._vector_cache` icinde sinif duzeyinde
   tutulur; her sorguda diskten yeniden okunmaz.

Onbellek, veri degistiren her yolda acikca gecersiz kilinir:
[database.py:393](../../database.py), [database.py:441](../../database.py),
[ingestion.py:260](../../ingestion.py).

## Gerekce

- Harici bir vektor veritabani (Chroma, FAISS, pgvector) projenin temel
  iddiasini zayiflatirdi: tek dosya, sunucusuz, tamamen cevrimdisi, kurulum
  gerektirmeyen dagitim. SQLite bu iddianin tasiyicisi.
- Bu olcekte (binlerce parca) matris carpimi zaten milisaniye mertebesinde;
  yaklasik komsu indeksi (ANN) karmasikligi kazanc getirmezdi.

## Sonuclar

- **Olcek siniri:** Tum vektorler RAM'de tutulur. Bellek kullanimi parca
  sayisiyla dogrusal artar. Yuz binlerce parcali bir kurumsal koleksiyonda bu
  yaklasim yeniden degerlendirilmelidir; bilinen ve kabul edilmis sinirdir.
- **Onbellek tutarliligi kritik hale geldi:** Onbellegi gecersiz kilmayi
  unutan yeni bir yazma yolu, sunucu yeniden baslatilana kadar yeni belgelerin
  gorunmemesine yol acar. Yeni bir yazma yolu eklendiginde
  `Retriever.invalidate_cache()` cagrisi zorunludur.
- Olcek davranisi `benchmark.py` ile olculebilir.
