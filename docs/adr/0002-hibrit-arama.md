# ADR-0002: Hibrit arama (dense embedding + BM25), RRF ile birlestirme

**Durum:** Kabul edildi
**Tarih:** 2026-07-21

## Baglam

Program plani retrieval icin saf dense yaklasimi tarif ediyordu: sorguyu
embed et, tum parcalarla kosinus benzerligi hesapla, en yuksek K taneyi al.

Turkce'de bu yaklasim sondan eklemeli yapi yuzunden zayifliyor. "izin" ile
"izinleri" veya "izne" farkli yuzey formlar; kucuk bir embedding modelinde bu
formlar arasindaki benzerlik, alakasiz ama tema olarak yakin bir parcanin
benzerliginin altinda kalabiliyor. Sonuc: kullanicinin tam olarak kullandigi
terimi iceren parca, ilk K'ye giremiyor.

## Karar

Retrieval iki ayakli calisir:

1. **Dense ayak:** NumPy matris carpimiyla kosinus benzerligi (`top_k * 5`
   buyuklugunde genis bir havuz cekilir).
2. **Sparse ayak:** BM25 tabanli anahtar kelime aramasi, on-ek eslesmesiyle.

Iki siralama **Reciprocal Rank Fusion (RRF)** ile birlestirilir
([search_fusion.py](../../search_fusion.py)).

## Gerekce

- Iki yontemin skorlari farkli olceklerde (kosinus 0-1 arasi, BM25 sinirsiz).
  Skorlari toplamak olcek kalibrasyonu gerektirir ve kirilgandir. RRF yalnizca
  **siralamalari** kullandigi icin olcek sorunundan bagimsizdir.
- Dense havuzun genis tutulmasi (`HYBRID_POOL_FACTOR=5`), anahtar kelime
  ayaginin siralamayi gercekten degistirebilmesi icin gereklidir; havuz `top_k`
  kadar dar olsaydi fuzyon hicbir sey degistiremezdi.

## Kritik nokta: anahtar kelime eslesmesi tek basina yeterli degildir

Kelime eslesen parcalar icin benzerlik esigi `KEYWORD_RESCUE_RATIO` (0.75)
carpani ile gevsetilir, ama **sifirlanmaz**. Eger kelime eslesmesi tek basina
yeterli sayilsaydi, "izin" kelimesi gecen her belge, izinle ilgisi olmayan her
soruya cevap olarak donerdi. Bu, RAG sistemlerinde en sik gorulen yanlis
pozitif kaynagidir.

Bu davranis `eval/questions.json` icindeki **tuzak** kategorisiyle test edilir:
anahtar kelimesi belgelerde gecen ama cevabi belgelerde olmayan sorular.

## Sonuclar

- Retrieval kodu saf dense'e gore belirgin sekilde karmasiklasti.
- `USE_HYBRID_SEARCH=false` ile tek satirda saf dense'e donulebilir; iki mod
  arasindaki fark eval seti ile olculebilir.
- Ayarlanmasi gereken uc yeni parametre dogdu: `HYBRID_POOL_FACTOR`,
  `KEYWORD_RESCUE_RATIO`, `MIN_SIMILARITY`. Bunlar birbirine bagli; birini
  degistirince eval seti yeniden calistirilmalidir.
