# Yanit Kalitesi Degerlendirmesi

## Neden ayri bir sey

`pytest tests/` **kodun** dogru calistigini gosterir. Gostermedigi sey:
asistanin **dogru cevap verdigi**. Bu iki soru bagimsizdir - 166 testi gecen
bir RAG sistemi pekala her soruya bilgi uydurabilir.

Bu klasor ikincisini olcer.

```bash
python eval/run_eval.py     # -> RESULTS.md
```

## Soru kategorileri

| Kategori | Ne olcuyor | Neden onemli |
|---|---|---|
| `cevaplanabilir` | Belgedeki bilgiyi dogru kaynakla bulabiliyor mu | Temel islev |
| `cevaplanamaz` | Belgede hic olmayan bilgiyi uydurmuyor mu | Guvenin dayandigi sey |
| `tuzak` | Anahtar kelimeler belgede geciyor ama **cevap yok** - yine de reddediyor mu | En zor durum; asagiya bakin |
| `kenar_durum` | Bos / bozuk / asiri genel girdide cokmuyor mu | Plan Faz 3 gereksinimi |

## Bulgu: reddetme kuralinin promptaki yeri sonucu degistiriyor

Ilk olcumde ([RESULTS-baseline-01.md](RESULTS-baseline-01.md)) belgedeki
sorularin neredeyse hepsi dogru cevaplaniyordu, ama **belgede olmayan sorularda
sistem bilgi uyduruyordu**. Ornekler:

> **Soru:** Ofisteki toplanti salonunun aylik kirasi ne kadar?
> **Yanit:** "Aylik toplanti salonunun kirasi, 2026 yili icin 240 TL'dir."

Belgelerde "kira" kelimesi yalnizca "arac kiralama" olarak geciyor. Rakam da,
yil da tamamen uydurma.

> **Soru:** Sirketin 2025 yili cirosu ne kadardir?
> **Yanit:** "2025 yili cirosu 14 isgunluclu yillik izne hak kazandirmaktadir."

Izin politikasindaki sayiyi ciro sorusuna yapistirmis.

**Kok neden:** Sistem promptunda "baglamda bilgi yoksa bilmiyorum de" kurali
**dorduncu ve son sirada** yaziyordu, ustelik prompt "sorusuna dogrudan ve net
bir yanit ver" cumlesiyle basliyordu. 1.5B parametreli bir model bu sirayla
karsilastiginda cevap vermeye yoneliyor ve son kurali yok sayiyor.

**Degisiklik:** Reddetme kontrolu promptun **en basina**, ilk kontrol olarak
tasindi; "baglam konuyla ilgili gorunse bile cevap orada yazmiyorsa reddet" ve
"baglamda gecmeyen sayi/tutar/tarih uretme" ifadeleri acikca eklendi.

### Sonuc

| Kategori | Once | Sonra |
|---|---|---|
| cevaplanabilir | 11 / 12 | 11 / 12 |
| cevaplanamaz | **1 / 4** | **3 / 4** |
| tuzak | 0 / 3 | 0 / 3 |
| **Genel** | **%60** | **%74** |

Onemli olan: reddetme iyilesirken **dogru cevaplarda kayip olmadi**. Bu, esik
degerini yukselterek elde edilen bir kazanc olsaydi, dogru cevaplardan da
kaybederdik.

## Cozulmemis: `tuzak` kategorisi 0/3

Geri kalan hatalar tek bir sinifta toplaniyor: **getirilen parcalar konuyla
gercekten ilgili, ama sorunun cevabini icermiyor.** Ornegin "toplanti salonu
kirasi" sorusunda `toplanti_ve_ofis_kurallari.txt` getiriliyor (benzerlik
0.482 - dogru cevaplarin cogundan yuksek), icinde toplanti salonu var, kira yok.

Bu iki ayri basarisizlik moduna isaret ediyor:

| Mod | Belirti | Dogru arac |
|---|---|---|
| Alakasiz parca esigi geciyor | Dusuk benzerlik (0.28-0.33) ama yine de LLM'e gidiyor | `MIN_SIMILARITY` / `KEYWORD_RESCUE_RATIO` kalibrasyonu |
| Ilgili ama yetersiz parca | Yuksek benzerlik (0.48), model bosluğu dolduruyor | Model kapasitesi / daha guclu prompt / cikti dogrulama |

## Neden esik degeri **bilerek** ayarlanmadi

Olcumler, `MIN_SIMILARITY` degerini 0.35'ten ~0.40'a cikarmanin kalan
basarisizliklarin bir kismini cozecegini gosteriyor. Bu yapilmadi, cunku:

- Elde yalnizca **23 soru** var ve hepsi ayarlama icin kullanilirsa, elde edilen
  esik bu 23 soruya **ezberlenmis** olur; gercek bir iyilesme oldugunu iddia
  edemeyiz.
- Dogru yontem, esigi ayarlamak icin ayri bir set, dogrulamak icin ayri bir set
  kullanmaktir. Bu set henuz yok.

Sunum oncesinde sayilari guzellestirmek icin esik oynatmak, olcumu anlamsiz
kilardi. Bulgu oldugu gibi birakildi.

## Sonraki adimlar

- [ ] Ayri bir dogrulama seti olusturup `MIN_SIMILARITY` ve
      `KEYWORD_RESCUE_RATIO` degerlerini kalibre et
- [ ] `tuzak` sinifi icin cikti dogrulama dene: modelin urettigi sayilarin
      baglamda gercekten gecip gecmedigini kontrol et
- [ ] Daha buyuk bir model (`phi-4-mini`) ile ayni seti calistirip farki olc

## Olcum notu

Guncel `RESULTS.md` **bos makinede** olculmustur ve `benchmark.py` ile
tutarlidir: medyan yanit 15.5 sn, bunun ~15.4 sn'si ilk token oncesi (CPU
embedding + baglam prefill), uretimin kendisi ~1 sn. 72 sn'lik uc deger olcum
hatasi degildir: modelin tekrar dongusune girip 1024 token'lik butceyi
tuketmesidir (dongu kesici ciktiyi temizler ama sureyi kurtaramaz,
bkz. ADR-0007). Kategori sonuclari iki bagimsiz kosuda ayni cikmistir;
olcum tekrarlanabilirdir.
