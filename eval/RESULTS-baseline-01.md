# Yanit Kalitesi Degerlendirme Sonuclari

Calistirma: 2026-07-21 13:31

Bu rapor `python eval/run_eval.py` ile uretilir. Unit testlerden farki:
kodun calistigini degil, asistanin **dogru cevap verdigini** olcer.

## Ozet

- Toplam soru: **23**
- Gecti: **12** / 20 otomatik puanlanan (%60)
- Kaldi: **8**
- Manuel inceleme: 3
- Medyan yanit suresi: **14.39 s**
- En yavas yanit: 25.18 s

### Kategori bazinda

| Kategori | Gecti / Toplam | Ne olcuyor |
|---|---|---|
| cevaplanabilir | 11 / 12 | Belgedeki bilgiyi bulup dogru kaynakla veriyor mu |
| cevaplanamaz | 1 / 4 | Belgede olmayan bilgiyi uydurmuyor mu |
| tuzak | 0 / 3 | Anahtar kelime eslesiyor ama cevap yok - yine de reddediyor mu |
| kenar_durum | 0 / 4 | Bozuk/asiri genel girdide cokmuyor mu |

## Soru bazinda sonuclar

| ID | Tip | Soru | Durum | Kaynak | Parca | Guven | Sure |
|---|---|---|---|---|---|---|---|
| C01 | cevaplanabilir | Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir? | **GECTI** | izin_politikasi.txt, ise_alim_oryantasyon.txt | 3 | 0.655 | 16.68s |
| C02 | cevaplanabilir | Izin talebi en az kac is gunu once girilmelidir? | **GECTI** | izin_politikasi.txt, vpn_ve_bt_sss.txt | 3 | 0.504 | 13.93s |
| C03 | cevaplanabilir | Evlilik durumunda kac is gunu ucretli mazeret izni verilir? | **GECTI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.612 | 14.61s |
| C04 | cevaplanabilir | Sehir ici is yemeklerinde kisi basi ust limit nedir? | **KALDI** | seyahat_politikasi.txt, masraf_politikasi.txt | 3 | 0.507 | 25.18s |
| C05 | cevaplanabilir | Musteri agirlama yemeklerinde kisi basi limit ne kadardir? | **GECTI** | masraf_politikasi.txt, seyahat_politikasi.txt | 3 | 0.485 | 13.45s |
| C06 | cevaplanabilir | Gecikmis masraf talepleri kac gun sonra odenmez? | **GECTI** | masraf_politikasi.txt, izin_politikasi.txt | 3 | 0.418 | 13.94s |
| C07 | cevaplanabilir | Haftada en fazla kac gun uzaktan calisabilirim? | **GECTI** | uzaktan_calisma.txt, politika.txt, toplanti_ve_ofis_kurallari.txt | 3 | 0.445 | 14.39s |
| C08 | cevaplanabilir | Hangi gun tum ekiplerin ofiste bulunmasi zorunludur? | **GECTI** | toplanti_ve_ofis_kurallari.txt, uzaktan_calisma.txt, etik_ve_uyum.txt | 3 | 0.429 | 14.30s |
| C09 | cevaplanabilir | Standart mesai saatleri nedir? | **GECTI** | uzaktan_calisma.txt, seyahat_politikasi.txt, masraf_politikasi.txt | 3 | 0.335 | 16.16s |
| C10 | cevaplanabilir | Kurumsal VPN istemcisinin adi nedir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, bilgi_guvenligi.txt | 3 | 0.488 | 13.46s |
| C11 | cevaplanabilir | VPN baglantisi kac saat sonra otomatik olarak sonlanir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt | 3 | 0.562 | 14.37s |
| C12 | cevaplanabilir | Standart dizustu bilgisayar yenileme suresi kac yildir? | **GECTI** | vpn_ve_bt_sss.txt, ise_alim_oryantasyon.txt | 3 | 0.597 | 15.51s |
| R01 | cevaplanamaz | Sirketin 2025 yili cirosu ne kadardir? | **KALDI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.304 | 16.35s |
| R02 | cevaplanamaz | Sirketin Paris ofisinin adresi nedir? | **GECTI** | politika.txt | 1 | 0.349 | 6.66s |
| R03 | cevaplanamaz | Calisanlara hisse senedi opsiyonu veriliyor mu? | **KALDI** | bilgi_guvenligi.txt, yan_haklar.txt, masraf_politikasi.txt | 3 | 0.322 | 15.95s |
| R04 | cevaplanamaz | Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, izin_politikasi.txt | 3 | 0.281 | 14.93s |
| T01 | tuzak | Yillik ciro hedefi ve kar marji nedir? | **KALDI** | izin_politikasi.txt, performans_degerlendirme.txt, masraf_politikasi.txt | 3 | 0.329 | 25.01s |
| T02 | tuzak | Ofisteki toplanti salonunun aylik kirasi ne kadar? | **KALDI** | toplanti_ve_ofis_kurallari.txt, yan_haklar.txt | 3 | 0.482 | 18.11s |
| T03 | tuzak | Izin gunlerinde VPN parolasi kac gunde bir degisir? | **KALDI** | vpn_ve_bt_sss.txt, bilgi_guvenligi.txt, uzaktan_calisma.txt | 3 | 0.455 | 20.07s |
| K01 | kenar_durum | _(bos)_ | **KALDI** | - | 0 | 0.000 | 0.00s |
| K02 | kenar_durum | ? | **INCELE** | - | 0 | 0.000 | 2.18s |
| K03 | kenar_durum | merhaba | **INCELE** | Hafta-6_ Mobil Ticaret.PDF, Erkan_Turgut_cv.pdf, izin_politikasi.txt | 3 | 0.410 | 13.69s |
| K04 | kenar_durum | Sirket hakkindaki her seyi bana tek tek anlat | **INCELE** | politika.txt, bilgi_guvenligi.txt, etik_ve_uyum.txt | 3 | 0.374 | 13.46s |

## Yanit detaylari

### C01 - GECTI

**Soru:** Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
İşte doğru cevap:

**14 isgun** 

İzin politikasına göre, yeni baslayan calisanlar ilk yilini doldurduktan sonra 14 isgun yillik izne hak kazanır.
```

### C02 - GECTI

**Soru:** Izin talebi en az kac is gunu once girilmelidir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
En az 5 isgunluclu talebimiz gerekecek.
```

### C03 - GECTI

**Soru:** Evlilik durumunda kac is gunu ucretli mazeret izni verilir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Ucretli mazeret izni evlilik durumunda 3 isgunluyla verilir.
```

### C04 - KALDI

**Soru:** Sehir ici is yemeklerinde kisi basi ust limit nedir?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['750'])

**Yanit:**

```
Kisi basi ust limit, sehir ici is yemeklerinde kullanılan üst sınırlı masraf politikasıdır. Bu politika, is yemeklerinde kullanılan masrafları sınırlarla gösterir ve bu sınırların altında olan masraflara genellikle özel gereksiz veya extra masraf türleri dahil olmak üzere özel masraf türlerini içerir. Kisi basi üst limit, genellikle is yemeklerinde kullanılan masraflara göre belirlenir ve bu masrafların genellikle özel gereksiz veya extra masraf türleri dahil olmak üzere özel masraf türlerini içerir. Bu tür masrafların genellikle özel gereksiz veya extra masraf türleri dahil olmak üzere özel masraf türlerini içerir. 

Limit kisi basi 1.500 TL'dir ve yonetici onayi gerekir. 

Alkollu icecek masrafları sirket tarafindan karsilanmaz.
```

### C05 - GECTI

**Soru:** Musteri agirlama yemeklerinde kisi basi limit ne kadardir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Musteri agirlama yemeklerinde limit kisi basi 1.500 TL'dir.
```

### C06 - GECTI

**Soru:** Gecikmis masraf talepleri kac gun sonra odenmez?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Geçikmis masraf talepleri 30 gün sonra odenmez.
```

### C07 - GECTI

**Soru:** Haftada en fazla kac gun uzaktan calisabilirim?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Haftada en fazla 2 gün uzaktan çalışabilirsiniz.
```

### C08 - GECTI

**Soru:** Hangi gun tum ekiplerin ofiste bulunmasi zorunludur?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Pazartesi günü tum ekiplerin ofiste bulunmasi zorunludur.
```

### C09 - GECTI

**Soru:** Standart mesai saatleri nedir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Standart mesai saatleri 09:00 - 18:00 arasıdır.
```

### C10 - GECTI

**Soru:** Kurumsal VPN istemcisinin adi nedir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
"SecureConnect"
```

### C11 - GECTI

**Soru:** VPN baglantisi kac saat sonra otomatik olarak sonlanir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
VPN baglantisi 12 saat sonra otomatik olarak sonlanır.
```

### C12 - GECTI

**Soru:** Standart dizustu bilgisayar yenileme suresi kac yildir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Standart dizustu bilgisayar yenileme süresi 3 yıldir.
```

### R01 - KALDI

**Soru:** Sirketin 2025 yili cirosu ne kadardir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
2025 yili cirosu 14 isgunluclu yillik izne hak kazandırmaktadır.
```

### R02 - GECTI

**Soru:** Sirketin Paris ofisinin adresi nedir?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
No information found in documents.
```

### R03 - KALDI

**Soru:** Calisanlara hisse senedi opsiyonu veriliyor mu?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Calisanlara hisse senedi opsiyonu verilmedi. Calisanlar için en az 40 saat boyunca eğitim alabileceklerdir. Yuksek lisans destegi için en az 2 yıl kidemeden önce gereklidir ve yillik üst sınıflimizin en az 60.000 TL gerektirir.
```

### R04 - KALDI

**Soru:** Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
CEO'nuz sirketin kurucusu ve başkanıdır. Sirket 1987 yılında kurulmuştur.
```

### T01 - KALDI

**Soru:** Yillik ciro hedefi ve kar marji nedir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Yillik ciro hedefi, ilk yilinizdaki ciro sayısını belirtir ve kidem 5 yili astiginda ciro 20 isgunluğuna çıkardı. Kidem 10 yili astiginda ise ciro 26 isgunluğuna çıkardı. 

Kar marji ise belgelemede belirtilen bir sonraki yılın ciro sayısına göre hesaplanır. Bu sonraki yılın ciro sayısının en az 5 isgunluğuna çıkması gerekiyor. 

Sonuç olarak, yillik ciro hedefi ise ilk yıldaki ciro sayısını belirtirken, kar marji ise belgelemede belirtilen bir sonraki yılın ciro sayısına göre hesaplanır.
```

### T02 - KALDI

**Soru:** Ofisteki toplanti salonunun aylik kirasi ne kadar?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Aylik toplanti salonunun kirasi, 2026 yili icin 240 TL'dir.
```

### T03 - KALDI

**Soru:** Izin gunlerinde VPN parolasi kac gunde bir degisir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
VPN parolaları 90 günde bir defada değiştirilmesi gerekmektedir. Ancak bu süre içinde parolaların ilk 5 defada tekrarı oluşturulması yasa dışıdır ve bu durumda güvenli bir şekilde kullanılmalıdır.
```

### K01 - KALDI

**Soru:** _(bos sorgu)_

**Degerlendirme:** istisna: ValueError: Input must be a non-empty string.

**Yanit:**

```
(bos)
```

### K02 - INCELE

**Soru:** ?

**Degerlendirme:** cokmedi, icerik manuel incelenmeli

**Yanit:**

```
Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### K03 - INCELE

**Soru:** merhaba

**Degerlendirme:** cokmedi, icerik manuel incelenmeli

**Yanit:**

```
Merhaba! Size nasıl yardımcı olabilirim?
```

### K04 - INCELE

**Soru:** Sirket hakkindaki her seyi bana tek tek anlat

**Degerlendirme:** cokmedi, icerik manuel incelenmeli

**Yanit:**

```
Tum calisanlar saat 09:00'da ise gelmelidir. Haftada 2 gün uzaktan çalışmalıdır.
```
