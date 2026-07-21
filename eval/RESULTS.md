# Yanit Kalitesi Degerlendirme Sonuclari

Calistirma: 2026-07-21 15:15

Bu rapor `python eval/run_eval.py` ile uretilir. Unit testlerden farki:
kodun calistigini degil, asistanin **dogru cevap verdigini** olcer.

## Ozet

- Toplam soru: **23**
- Gecti: **14** / 19 otomatik puanlanan (%74)
- Kaldi: **5**
- Manuel inceleme: 4
- Medyan yanit suresi: **15.51 s**
- En yavas yanit: 72.70 s

### Kategori bazinda

| Kategori | Gecti / Toplam | Ne olcuyor |
|---|---|---|
| cevaplanabilir | 11 / 12 | Belgedeki bilgiyi bulup dogru kaynakla veriyor mu |
| cevaplanamaz | 3 / 4 | Belgede olmayan bilgiyi uydurmuyor mu |
| tuzak | 0 / 3 | Anahtar kelime eslesiyor ama cevap yok - yine de reddediyor mu |
| kenar_durum | 0 / 4 | Bozuk/asiri genel girdide cokmuyor mu |

## Soru bazinda sonuclar

| ID | Tip | Soru | Durum | Kaynak | Parca | Guven | Sure |
|---|---|---|---|---|---|---|---|
| C01 | cevaplanabilir | Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir? | **GECTI** | izin_politikasi.txt, ise_alim_oryantasyon.txt | 3 | 0.655 | 16.75s |
| C02 | cevaplanabilir | Izin talebi en az kac is gunu once girilmelidir? | **GECTI** | izin_politikasi.txt, vpn_ve_bt_sss.txt | 3 | 0.504 | 15.84s |
| C03 | cevaplanabilir | Evlilik durumunda kac is gunu ucretli mazeret izni verilir? | **GECTI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.612 | 15.23s |
| C04 | cevaplanabilir | Sehir ici is yemeklerinde kisi basi ust limit nedir? | **KALDI** | seyahat_politikasi.txt, masraf_politikasi.txt | 3 | 0.507 | 24.48s |
| C05 | cevaplanabilir | Musteri agirlama yemeklerinde kisi basi limit ne kadardir? | **GECTI** | masraf_politikasi.txt, seyahat_politikasi.txt | 3 | 0.485 | 13.69s |
| C06 | cevaplanabilir | Gecikmis masraf talepleri kac gun sonra odenmez? | **GECTI** | masraf_politikasi.txt, izin_politikasi.txt | 3 | 0.418 | 15.36s |
| C07 | cevaplanabilir | Haftada en fazla kac gun uzaktan calisabilirim? | **GECTI** | uzaktan_calisma.txt, politika.txt, toplanti_ve_ofis_kurallari.txt | 3 | 0.445 | 15.29s |
| C08 | cevaplanabilir | Hangi gun tum ekiplerin ofiste bulunmasi zorunludur? | **GECTI** | toplanti_ve_ofis_kurallari.txt, uzaktan_calisma.txt, etik_ve_uyum.txt | 3 | 0.429 | 15.51s |
| C09 | cevaplanabilir | Standart mesai saatleri nedir? | **GECTI** | uzaktan_calisma.txt, seyahat_politikasi.txt, masraf_politikasi.txt | 3 | 0.335 | 16.65s |
| C10 | cevaplanabilir | Kurumsal VPN istemcisinin adi nedir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, bilgi_guvenligi.txt | 3 | 0.488 | 14.30s |
| C11 | cevaplanabilir | VPN baglantisi kac saat sonra otomatik olarak sonlanir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt | 3 | 0.562 | 15.64s |
| C12 | cevaplanabilir | Standart dizustu bilgisayar yenileme suresi kac yildir? | **GECTI** | vpn_ve_bt_sss.txt, ise_alim_oryantasyon.txt | 3 | 0.597 | 15.71s |
| R01 | cevaplanamaz | Sirketin 2025 yili cirosu ne kadardir? | **GECTI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.304 | 16.31s |
| R02 | cevaplanamaz | Sirketin Paris ofisinin adresi nedir? | **GECTI** | politika.txt | 1 | 0.349 | 8.86s |
| R03 | cevaplanamaz | Calisanlara hisse senedi opsiyonu veriliyor mu? | **GECTI** | bilgi_guvenligi.txt, yan_haklar.txt, masraf_politikasi.txt | 3 | 0.322 | 14.75s |
| R04 | cevaplanamaz | Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, izin_politikasi.txt | 3 | 0.281 | 17.93s |
| T01 | tuzak | Yillik ciro hedefi ve kar marji nedir? | **KALDI** | izin_politikasi.txt, performans_degerlendirme.txt, masraf_politikasi.txt | 3 | 0.329 | 72.70s |
| T02 | tuzak | Ofisteki toplanti salonunun aylik kirasi ne kadar? | **KALDI** | toplanti_ve_ofis_kurallari.txt, yan_haklar.txt | 3 | 0.482 | 33.24s |
| T03 | tuzak | Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt | 3 | 0.507 | 20.06s |
| K01 | kenar_durum | _(bos)_ | **INCELE** | - | 0 | 0.000 | 0.00s |
| K02 | kenar_durum | ? | **INCELE** | - | 0 | 0.000 | 1.90s |
| K03 | kenar_durum | merhaba | **INCELE** | Hafta-6_ Mobil Ticaret.PDF, Erkan_Turgut_cv.pdf, izin_politikasi.txt | 3 | 0.410 | 13.80s |
| K04 | kenar_durum | Sirket hakkindaki her seyi bana tek tek anlat | **INCELE** | politika.txt, bilgi_guvenligi.txt, etik_ve_uyum.txt | 3 | 0.374 | 12.78s |

## Yanit detaylari

### C01 - GECTI

**Soru:** Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
14 isgunluğuna hak kazanır.
```

### C02 - GECTI

**Soru:** Izin talebi en az kac is gunu once girilmelidir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
En az 5 isgunluce talebilmelidir.
```

### C03 - GECTI

**Soru:** Evlilik durumunda kac is gunu ucretli mazeret izni verilir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
3 isgun
```

### C04 - KALDI

**Soru:** Sehir ici is yemeklerinde kisi basi ust limit nedir?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['750'])

**Yanit:**

```
1. Yalnizca BAGLAM'daki gercekleri kullan.
2. Kullanicinin sordugu dilde (Turkce soruya Turkce, Ingilizce soruya Ingilizce) kisa ve net yaz.
3. Kullandigin bilginin sonuna [Kaynak: dosya_adi] ekle.

Sonucu:

**Limit uzunluğunu ve kisi basıncını belirtir:** 
- **Ust limit**: 1.500 TL
- **Kisi basıncı**: 10 gün içinde belgeleme gereklidir. 

**Sonuç:** 
*Sehir ici is yemeklerinde kisi basi ust limit 1.500 TL'dir.*

**Sonuç Kaynak:** 
masraf_politikasi.txt
```

### C05 - GECTI

**Soru:** Musteri agirlama yemeklerinde kisi basi limit ne kadardir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
1.500 TL'dir.
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
OTOMATİK SONLANMA SAATI: 12 SAAHARDA OTOMATİK ÇALIŞMADAN SONRA.
```

### C12 - GECTI

**Soru:** Standart dizustu bilgisayar yenileme suresi kac yildir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
3 yıldır
```

### R01 - GECTI

**Soru:** Sirketin 2025 yili cirosu ne kadardir?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### R02 - GECTI

**Soru:** Sirketin Paris ofisinin adresi nedir?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### R03 - GECTI

**Soru:** Calisanlara hisse senedi opsiyonu veriliyor mu?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### R04 - KALDI

**Soru:** Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Üzgünüz, bu bilgilerimizle ilgili bilgim yoktur. Ancak, şirketin kuruluş tarihi ve CEO'nun kim olduğunu öğrenmek için daha fazlasını aramak gerekir. Bu bilgileri aramak için internet üzerinden araştırma yapmanızı öneririm.
```

### T01 - KALDI

**Soru:** Yillik ciro hedefi ve kar marji nedir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Kar Marji: Yillik Ciro Hedefi

- **Hedef**: Birçok iş için gereken ciro ve tedavilerin bir örneği olan yillik ciro hedefi, bir kişinin yıldızlık veya bir işe sahip olması için gereklidir.

- **Kar Marji**: Kar Marji, bir kişinin yıldızlık veya bir işe sahip olması için gereklidir. Kar Marj
```

### T02 - KALDI

**Soru:** Ofisteki toplanti salonunun aylik kirasi ne kadar?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Aylik toplanti salonunun kirasi, sirket tarafından belirlenen ve toplanti salonunda kullanılan ve kullanımları düzenlenebilen özel bir alandır. Bu nedenle,
```

### T03 - KALDI

**Soru:** Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Bu bilgiye ulaşılamadım. Kurumsal VPN için en uygun bilgi kaynağınsanız, bu bilgilerle ilgili daha detaylı bilgi alabilmecin.
```

### K01 - INCELE

**Soru:** _(bos sorgu)_

**Degerlendirme:** cokmedi, icerik manuel incelenmeli

**Yanit:**

```
Lutfen bir soru yazin.
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
Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```
