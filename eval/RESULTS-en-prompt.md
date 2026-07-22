# Yanit Kalitesi Degerlendirme Sonuclari

Calistirma: 2026-07-22 08:33

Bu rapor `python eval/run_eval.py` ile uretilir. Unit testlerden farki:
kodun calistigini degil, asistanin **dogru cevap verdigini** olcer.

## Ozet

- Toplam soru: **23**
- Gecti: **12** / 19 otomatik puanlanan (%63)
- Kaldi: **7**
- Manuel inceleme: 4
- Medyan yanit suresi: **14.96 s**
- En yavas yanit: 70.63 s

### Kategori bazinda

| Kategori | Gecti / Toplam | Ne olcuyor |
|---|---|---|
| cevaplanabilir | 9 / 12 | Belgedeki bilgiyi bulup dogru kaynakla veriyor mu |
| cevaplanamaz | 2 / 4 | Belgede olmayan bilgiyi uydurmuyor mu |
| tuzak | 1 / 3 | Anahtar kelime eslesiyor ama cevap yok - yine de reddediyor mu |
| kenar_durum | 0 / 4 | Bozuk/asiri genel girdide cokmuyor mu |

## Soru bazinda sonuclar

| ID | Tip | Soru | Durum | Kaynak | Parca | Guven | Sure |
|---|---|---|---|---|---|---|---|
| C01 | cevaplanabilir | Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir? | **KALDI** | izin_politikasi.txt, ise_alim_oryantasyon.txt | 3 | 0.655 | 17.22s |
| C02 | cevaplanabilir | Izin talebi en az kac is gunu once girilmelidir? | **GECTI** | izin_politikasi.txt, vpn_ve_bt_sss.txt | 3 | 0.504 | 17.02s |
| C03 | cevaplanabilir | Evlilik durumunda kac is gunu ucretli mazeret izni verilir? | **GECTI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.612 | 13.32s |
| C04 | cevaplanabilir | Sehir ici is yemeklerinde kisi basi ust limit nedir? | **GECTI** | seyahat_politikasi.txt, masraf_politikasi.txt | 3 | 0.507 | 14.76s |
| C05 | cevaplanabilir | Musteri agirlama yemeklerinde kisi basi limit ne kadardir? | **KALDI** | masraf_politikasi.txt, seyahat_politikasi.txt | 3 | 0.485 | 13.37s |
| C06 | cevaplanabilir | Gecikmis masraf talepleri kac gun sonra odenmez? | **KALDI** | masraf_politikasi.txt, izin_politikasi.txt | 3 | 0.418 | 14.46s |
| C07 | cevaplanabilir | Haftada en fazla kac gun uzaktan calisabilirim? | **GECTI** | uzaktan_calisma.txt, politika.txt, toplanti_ve_ofis_kurallari.txt | 3 | 0.445 | 14.88s |
| C08 | cevaplanabilir | Hangi gun tum ekiplerin ofiste bulunmasi zorunludur? | **GECTI** | toplanti_ve_ofis_kurallari.txt, uzaktan_calisma.txt, etik_ve_uyum.txt | 3 | 0.429 | 14.96s |
| C09 | cevaplanabilir | Standart mesai saatleri nedir? | **GECTI** | uzaktan_calisma.txt, seyahat_politikasi.txt, yan_haklar.txt | 3 | 0.335 | 17.15s |
| C10 | cevaplanabilir | Kurumsal VPN istemcisinin adi nedir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, bilgi_guvenligi.txt | 3 | 0.488 | 15.01s |
| C11 | cevaplanabilir | VPN baglantisi kac saat sonra otomatik olarak sonlanir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt | 3 | 0.562 | 16.80s |
| C12 | cevaplanabilir | Standart dizustu bilgisayar yenileme suresi kac yildir? | **GECTI** | vpn_ve_bt_sss.txt, ise_alim_oryantasyon.txt | 3 | 0.597 | 16.38s |
| R01 | cevaplanamaz | Sirketin 2025 yili cirosu ne kadardir? | **KALDI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.304 | 16.09s |
| R02 | cevaplanamaz | Sirketin Paris ofisinin adresi nedir? | **GECTI** | politika.txt | 1 | 0.349 | 7.13s |
| R03 | cevaplanamaz | Calisanlara hisse senedi opsiyonu veriliyor mu? | **GECTI** | bilgi_guvenligi.txt, yan_haklar.txt, masraf_politikasi.txt | 3 | 0.322 | 13.64s |
| R04 | cevaplanamaz | Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, izin_politikasi.txt | 3 | 0.281 | 68.48s |
| T01 | tuzak | Yillik ciro hedefi ve kar marji nedir? | **KALDI** | izin_politikasi.txt, performans_degerlendirme.txt, masraf_politikasi.txt | 3 | 0.329 | 70.63s |
| T02 | tuzak | Ofisteki toplanti salonunun aylik kirasi ne kadar? | **KALDI** | toplanti_ve_ofis_kurallari.txt, yan_haklar.txt | 3 | 0.482 | 15.54s |
| T03 | tuzak | Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt | 3 | 0.507 | 16.14s |
| K01 | kenar_durum | _(bos)_ | **INCELE** | - | 0 | 0.000 | 0.00s |
| K02 | kenar_durum | ? | **INCELE** | - | 0 | 0.000 | 4.38s |
| K03 | kenar_durum | merhaba | **INCELE** | izin_politikasi.txt, ise_alim_oryantasyon.txt | 3 | 0.366 | 14.19s |
| K04 | kenar_durum | Sirket hakkindaki her seyi bana tek tek anlat | **INCELE** | politika.txt, bilgi_guvenligi.txt, ise_alim_oryantasyon.txt | 3 | 0.374 | 11.83s |

## Yanit detaylari

### C01 - KALDI

**Soru:** Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['14'])

**Yanit:**

```
"Kidem 5 yili astiginda yillik izin 20 is gunune, 10 yili astiginda 26 is gunune cikar."
```

### C02 - GECTI

**Soru:** Izin talebi en az kac is gunu once girilmelidir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
"IZIN TALEBI SURECI"
Izin talepleri Insan Kaynaklari portali uzerinden, izin baslangic tarihinden en az 5 is gunu once girilmelidir. Talep, once birim yoneticisi tarafindan onaylanir, ardindan Insan Kaynaklari tarafindan sisteme islenir. Onaylanmamis izinler kullanilamaz.
```

### C03 - GECTI

**Soru:** Evlilik durumunda kac is gunu ucretli mazeret izni verilir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
3 isgun
```

### C04 - GECTI

**Soru:** Sehir ici is yemeklerinde kisi basi ust limit nedir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
"Sehir ici is yemeklerinde kisi basi ust limit 750 TL'dir."
```

### C05 - KALDI

**Soru:** Musteri agirlama yemeklerinde kisi basi limit ne kadardir?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['1.500', '1500'])

**Yanit:**

```
"Sehir ici is yemeklerinde kisi basi ust limit 750 TL'dir."
```

### C06 - KALDI

**Soru:** Gecikmis masraf talepleri kac gun sonra odenmez?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['30'])

**Yanit:**

```
"Geckmis masraf talepleri odenmez."
```

### C07 - GECTI

**Soru:** Haftada en fazla kac gun uzaktan calisabilirim?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
"Haftada en fazla 2 gün uzaktan çalışabilir." Bu bilginin context'te yer aldığı için bu bilgiyi yanıtladım.
```

### C08 - GECTI

**Soru:** Hangi gun tum ekiplerin ofiste bulunmasi zorunludur?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Pazartesi günü tum ekiplerin ofiste bulunması zorunludır.
```

### C09 - GECTI

**Soru:** Standart mesai saatleri nedir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
"Standart mesai saatleri 09:00 - 18:00 arasıdır."
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
"VPN baglantisi 12 saat sonra otomatik olarak sonlanır."
```

### C12 - GECTI

**Soru:** Standart dizustu bilgisayar yenileme suresi kac yildir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
"Standart dizustu bilgisayar yenileme süresi 3 yıldır." Bu bilginin Türkçe karşılığıdır.
```

### R01 - KALDI

**Soru:** Sirketin 2025 yili cirosu ne kadardir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
"Devreden izinler Mart ayi sonuna kadar kullanilmalidir."
```

### R02 - GECTI

**Soru:** Sirketin Paris ofisinin adresi nedir?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
"Paris Ofisi" adlı sirketin adresi belirtilmediği için, bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### R03 - GECTI

**Soru:** Calisanlara hisse senedi opsiyonu veriliyor mu?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
"Calisanlara hisse senedi opsiyonu veriliyor mu?" Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### R04 - KALDI

**Soru:** Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
"CEO" kelimesinin Türkçe karşılığı "Kurumsal CEO" olacaktır.

Birçok soruşturulan soruların cevaplarını bulmak için bu dosyaları okuma işlemi gerçekleştiriyoruz:

- **[PARCA 1]** dosyasında, **"SecureConnect"** adlı bir paket indirilmesi ve **"Active Directory parolası"** ile kullanıcının giriş yapması hakkında bilgi veriyor.
- **[PARCA 2]** dosyasında, **"Insan Kaynakları"** ile ilgili bilgilere ulaşmak için **"Donanim Talebi"** formunu açıklıyor.
- **[PARCA 3
```

### T01 - KALDI

**Soru:** Yillik ciro hedefi ve kar marji nedir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
"Yillik izinler bir sonraki yila en fazla 5 gun devredilebilir; devreden izinler Mart ayi sonuna kadar kullanilmalidir." Bu bilginin Türkçe karşılığıdır. 

Sonuç olarak, yillik izinler için Mart ayı sonuna kadar kullanılması ve bu süre zarfında devredeceği izinlerin maksimum 5 gün olması gerektiği bulunmaktadır. Ayrıca, yillik izinler genellikle ikinci yıldır alınır ve bu yıldır ise 14 günlik izinlerdir. 

Bu bilgilere göre
```

### T02 - KALDI

**Soru:** Ofisteki toplanti salonunun aylik kirasi ne kadar?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
"Toplanti Salonu Aylik Kirasi": 240 TL
```

### T03 - GECTI

**Soru:** Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
"Bu konuda elimdeki belgelerde bilgi bulunmuyor."
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
