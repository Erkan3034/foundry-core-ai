# ADR-0007: Tekrar dongusu savunmasi - orneklemeden deterministik tespite

**Durum:** Kabul edildi
**Tarih:** 2026-07-21

## Baglam

1.5B parametreli chat modeli, belirli sorularda kelime/cumle donguleri
uretiyordu: ayni ifadeyi bitmeyecek sekilde tekrar edip token butcesini
tuketiyor, kullaniciya bozuk yanit doniyordu.

Ilk cozum orneklemeye mudahaleydi: `FREQUENCY_PENALTY=0.3`. Bu, tekrarlayan
token'larin olasiligini dusurerek donguyu kiriyordu. Ancak bu cozumun dar bir
calisma araligi vardi:

- `0.4` ve uzeri: ciktinin genel kalitesi bozuluyor.
- Tam `0` gonderilmesi: modelin yalnizca noktalama uretmesine yol aciyor -
  bu yuzden kod, deger 0 ise parametreyi **hic gondermiyor**
  ([rag_engine.py:92](../../rag_engine.py)).

Yani cozum, dar bir aralikta ayarlanmis ve modele ozgu bir orneklemeye
bagimliydi. Model degistiginde yeniden ayarlanmasi gerekecekti.

## Karar

Tekrar dongusune karsi savunma **deterministik tespite** tasindi:

- Streaming yolunda uretilen metnin son 16 karakteri, o ana kadarki ciktida
  3 veya daha fazla kez geciyorsa uretim kesilir ve olay loglanir
  ([rag_engine.py:246](../../rag_engine.py)).
- Streaming olmayan yolda ardisik ayni satirlar `_clean_response` icinde
  temizlenir.

`FREQUENCY_PENALTY` varsayilani `0.0`'a (kapali) alindi; parametre
yapilandirilabilir olarak korundu.

## Gerekce

- Orneklemeye dayali cozum modele ozgudur ve olcusu yoktur: "0.3 iyi, 0.4 kotu"
  bilgisi deneysel ve kirilgandir. Model degisince gecersizlesir.
- Deterministik tespit model-bagimsizdir ve **gozlemlenebilirdir**: dongu
  yakalandiginda log kaydi dusuyor. Sorunun ne siklikta yasandigi olculebilir.
- Uretim kalitesi orneklemeye mudahale ile bozulmuyor.

## Sonuclar

- Dongu artik **onlenmiyor, kesiliyor**. Kullanici, dongu yakalandiginda yarim
  kalmis bir yanit gorebilir. Bu, sonsuz tekrara gore iyi ama mukemmel degil.
- Esik degerleri (16 karakter, 3 tekrar) sabit kodlu. Mesru sekilde tekrar eden
  kisa metinlerde (or. madde isaretli listeler, tablo benzeri ciktilar) yanlis
  pozitif verme ihtimali var. `eval/questions.json` icindeki `K04` (asiri genel
  soru) bu riski sinar.
## Guncelleme: iki yol birlestirildi

Ilk uygulamada tespit **yalnizca streaming** yolunda vardi; streaming olmayan
`/query` yolunda sadece ardisik ayni **satirlar** temizleniyordu, paragraf ici
dongu yakalanmiyordu.

Bu teorik bir eksik degildi. Degerlendirmede `C04` sorusu ("sehir ici is
yemeklerinde kisi basi ust limit") tam olarak bu yuzden basarisiz oldu: model
ayni cumleyi ucuncu kez tekrarlayip token butcesini tuketti ve ardindan **yanlis
rakami** verdi (750 yerine 1.500).

Ayrica bu, olcum acisindan daha ciddi bir sorun yaratiyordu: degerlendirme
streaming olmayan yolu olcuyor, kullanici arayuzu ise streaming yolunu
kullaniyor. Iki yol farkli davrandigi surece olculen sey kullanicinin gordugu
sey degildi.

`_truncate_repetition_loop` her iki yolda da ayni `_LOOP_WINDOW` /
`_LOOP_THRESHOLD` sabitlerini kullanacak sekilde ortaklastirildi
(`tests/test_rag.py::TestRepetitionLoopGuard`).

## Acik is

- [ ] Esik degerleri (16 karakter, 3 tekrar) sabit kodlu; yapilandirilabilir
      hale getirilmeli veya genisletilmis bir eval seti ile dogrulanmali.
- [ ] Streaming olmayan yolda kesme **uretimden sonra** yapiliyor; dongu yine de
      token butcesini tuketiyor. Uretim sirasinda durdurma (stopping criteria)
      arastirilmali - `C04` bu yuzden hala yanlis cevap veriyor.
- [ ] `FREQUENCY_PENALTY=0` iken modelin yalnizca noktalama uretmesi davranisi
      dogrulanmali: bu gercekten `0` gonderilmesinden mi kaynaklaniyordu, yoksa
      baska bir yapilandirma hatasiyla mi karisti? Kod bugun 0'i hic gondermedigi
      icin bu varsayim aktif olarak test edilmiyor.
