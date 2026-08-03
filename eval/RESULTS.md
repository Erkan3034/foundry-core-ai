# Yanit Kalitesi Degerlendirme Sonuclari

Calistirma: 2026-08-03 15:55

Bu rapor `python eval/run_eval.py` ile uretilir. Unit testlerden farki:
kodun calistigini degil, asistanin **dogru cevap verdigini** olcer.

## Ozet

- Toplam soru: **23**
- Gecti: **7** / 19 otomatik puanlanan (%37)
- Kaldi: **12**
- Manuel inceleme: 4
- Medyan yanit suresi: **13.55 s**
- En yavas yanit: 60.07 s

### Kategori bazinda

| Kategori | Gecti / Toplam | Ne olcuyor |
|---|---|---|
| cevaplanabilir | 6 / 12 | Belgedeki bilgiyi bulup dogru kaynakla veriyor mu |
| cevaplanamaz | 0 / 4 | Belgede olmayan bilgiyi uydurmuyor mu |
| tuzak | 1 / 3 | Anahtar kelime eslesiyor ama cevap yok - yine de reddediyor mu |
| kenar_durum | 0 / 4 | Bozuk/asiri genel girdide cokmuyor mu |

## Soru bazinda sonuclar

| ID | Tip | Soru | Durum | Kaynak | Parca | Guven | Sure |
|---|---|---|---|---|---|---|---|
| C01 | cevaplanabilir | Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir? | **KALDI** | izin_politikasi.txt, ise_alim_oryantasyon.txt, yan_haklar.txt | 4 | 0.655 | 11.50s |
| C02 | cevaplanabilir | Izin talebi en az kac is gunu once girilmelidir? | **GECTI** | izin_politikasi.txt, vpn_ve_bt_sss.txt, bilgi_guvenligi.txt | 4 | 0.504 | 10.94s |
| C03 | cevaplanabilir | Evlilik durumunda kac is gunu ucretli mazeret izni verilir? | **GECTI** | izin_politikasi.txt, yan_haklar.txt, masraf_politikasi.txt | 4 | 0.612 | 9.81s |
| C04 | cevaplanabilir | Sehir ici is yemeklerinde kisi basi ust limit nedir? | **GECTI** | seyahat_politikasi.txt, masraf_politikasi.txt | 4 | 0.507 | 11.22s |
| C05 | cevaplanabilir | Musteri agirlama yemeklerinde kisi basi limit ne kadardir? | **KALDI** | masraf_politikasi.txt, seyahat_politikasi.txt | 4 | 0.485 | 17.20s |
| C06 | cevaplanabilir | Gecikmis masraf talepleri kac gun sonra odenmez? | **KALDI** | masraf_politikasi.txt, izin_politikasi.txt, yan_haklar.txt | 4 | 0.418 | 10.41s |
| C07 | cevaplanabilir | Haftada en fazla kac gun uzaktan calisabilirim? | **KALDI** | uzaktan_calisma.txt, politika.txt, toplanti_ve_ofis_kurallari.txt | 4 | 0.445 | 23.08s |
| C08 | cevaplanabilir | Hangi gun tum ekiplerin ofiste bulunmasi zorunludur? | **KALDI** | toplanti_ve_ofis_kurallari.txt, uzaktan_calisma.txt, etik_ve_uyum.txt | 4 | 0.429 | 9.27s |
| C09 | cevaplanabilir | Standart mesai saatleri nedir? | **GECTI** | uzaktan_calisma.txt, seyahat_politikasi.txt, yan_haklar.txt, masraf_politikasi.txt | 4 | 0.335 | 11.91s |
| C10 | cevaplanabilir | Kurumsal VPN istemcisinin adi nedir? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, bilgi_guvenligi.txt | 4 | 0.488 | 15.25s |
| C11 | cevaplanabilir | VPN baglantisi kac saat sonra otomatik olarak sonlanir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, ise_alim_oryantasyon.txt | 4 | 0.562 | 13.55s |
| C12 | cevaplanabilir | Standart dizustu bilgisayar yenileme suresi kac yildir? | **GECTI** | vpn_ve_bt_sss.txt, ise_alim_oryantasyon.txt | 4 | 0.597 | 23.61s |
| R01 | cevaplanamaz | Sirketin 2025 yili cirosu ne kadardir? | **KALDI** | izin_politikasi.txt, yan_haklar.txt, performans_degerlendirme.txt | 4 | 0.304 | 23.40s |
| R02 | cevaplanamaz | Sirketin Paris ofisinin adresi nedir? | **KALDI** | politika.txt | 1 | 0.349 | 14.43s |
| R03 | cevaplanamaz | Calisanlara hisse senedi opsiyonu veriliyor mu? | **KALDI** | bilgi_guvenligi.txt, yan_haklar.txt, masraf_politikasi.txt | 4 | 0.322 | 60.07s |
| R04 | cevaplanamaz | Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, izin_politikasi.txt, yan_haklar.txt | 4 | 0.281 | 34.41s |
| T01 | tuzak | Yillik ciro hedefi ve kar marji nedir? | **KALDI** | izin_politikasi.txt, performans_degerlendirme.txt, masraf_politikasi.txt, yan_haklar.txt | 4 | 0.329 | 15.68s |
| T02 | tuzak | Ofisteki toplanti salonunun aylik kirasi ne kadar? | **GECTI** | toplanti_ve_ofis_kurallari.txt, yan_haklar.txt, masraf_politikasi.txt | 4 | 0.482 | 17.38s |
| T03 | tuzak | Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, bilgi_guvenligi.txt | 4 | 0.507 | 16.33s |
| K01 | kenar_durum | _(bos)_ | **INCELE** | - | 0 | 0.000 | 0.00s |
| K02 | kenar_durum | ? | **INCELE** | - | 0 | 0.000 | 5.06s |
| K03 | kenar_durum | merhaba | **INCELE** | izin_politikasi.txt, ise_alim_oryantasyon.txt | 3 | 0.366 | 12.94s |
| K04 | kenar_durum | Sirket hakkindaki her seyi bana tek tek anlat | **INCELE** | politika.txt, bilgi_guvenligi.txt, ise_alim_oryantasyon.txt, etik_ve_uyum.txt | 4 | 0.374 | 11.27s |

## Yanit detaylari

### C01 - KALDI

**Soru:** Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['14'])

**Yanit:**

```
Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### C02 - GECTI

**Soru:** Izin talebi en az kac is gunu once girilmelidir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Bilgilere göre, İzin Talebi en az 5 is gunu once girilmelidir.
```

### C03 - GECTI

**Soru:** Evlilik durumunda kac is gunu ucretli mazeret izni verilir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Evlilik durumunda, 3 is gunu ucretli mazeret izni verilir.
```

### C04 - GECTI

**Soru:** Sehir ici is yemeklerinde kisi basi ust limit nedir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Sehir ici is yemeklerinde kisi basi ust limit 750 TL'dir.
```

### C05 - KALDI

**Soru:** Musteri agirlama yemeklerinde kisi basi limit ne kadardir?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['1.500', '1500'])

**Yanit:**

```
Bu bilgilendirme bilgisini kaybettiğiniz senin bilgiye göre bu bilgi konusunda ilginç ve uygun şekilde kabul edilmesi için, bu bilgi konusundaki bilgi verilerini koruması gereken bir nokta olup, bu konusunda ilginç ve uygun şekilde kodlayabilirim. Bu bilgilendirme bilgisini kaybetteğiniz senin bilgiye göre
```

### C06 - KALDI

**Soru:** Gecikmis masraf talepleri kac gun sonra odenmez?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['30'])

**Yanit:**

```
Bu konuda elimdeki belgelerde bilgi bulunmuyor.
```

### C07 - KALDI

**Soru:** Haftada en fazla kac gun uzaktan calisabilirim?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['2'])

**Yanit:**

```
Bu bilgilendirme konusu soruna göre, bu bilgi genellikle genel turkce kitaplarında ve genel bir bilgi için kullanılamaz. Bu bilgilendirme konusunda genel turkce kitaplarında ve genel bir bilgi için kullanılamaz.
```

### C08 - KALDI

**Soru:** Hangi gun tum ekiplerin ofiste bulunmasi zorunludur?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['Pazartesi'])

**Yanit:**

```
Günevarli ofiste bulunmasi zorunludur.
```

### C09 - GECTI

**Soru:** Standart mesai saatleri nedir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Standart mesai saatleri 09:00 - 18:00 arasidir.
```

### C10 - KALDI

**Soru:** Kurumsal VPN istemcisinin adi nedir?

**Degerlendirme:** kaynak dogru, beklenen deger yok (['SecureConnect'])

**Yanit:**

```
BAGLAM'da genellikle "vpn_ve_bt_sss.txt" dosyanı kullanır ve bu dosya içindeki tüm bilgilere göre kurumsal ve buğdayalarda IP adresi ve telərəni bilintir. Bu bilgilere göre, BAGLAM'da genellikle "bt_destek@sirket.com" adını kullanır.
```

### C11 - GECTI

**Soru:** VPN baglantisi kac saat sonra otomatik olarak sonlanir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
VPN baglantisi 12 saat sonra otomatik olarak sonlanır ve bunu daha sonra 4 saat sonucunda sonlandı.
```

### C12 - GECTI

**Soru:** Standart dizustu bilgisayar yenileme suresi kac yildir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
Dizustu bilgisayar yenileme suresi 3 yıldır.
```

### R01 - KALDI

**Soru:** Sirketin 2025 yili cirosu ne kadardir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Bilgilere göre, 2025 yılı 2026 yılından 26 gün boyunca ilerleyebilir. Bu da 26 günlik ve 26 günlik arasında geçecek.
```

### R02 - KALDI

**Soru:** Sirketin Paris ofisinin adresi nedir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Bilginizde bulunmayan bilgilere sahip olmaksızdı. Sirketin Paris ofisinin adresi bilgisini verilmek için başka bir bilgiye ihtiyacım var.
```

### R03 - KALDI

**Soru:** Calisanlara hisse senedi opsiyonu veriliyor mu?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Yaşayan ve geçişten sonra sadece senin bilgiye ulaşmakta.
```

### R04 - KALDI

**Soru:** Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Bu sorunu tam olarak genellikle Sirketin CEO'ı ve Sirket'in kurulması için bir yılı notayı vermektedir. Ancak bu bilgilere ulaşmak için Sirketin hizmet listesindeki Sirket Yönetimi ve Sirket Yönetimi Listesi notları kullanmak gerekmektedir. Ayrıca
```

### T01 - KALDI

**Soru:** Yillik ciro hedefi ve kar marji nedir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Bu bilgilere göre, ilginç ilerel ilerliyor musun?
```

### T02 - GECTI

**Soru:** Ofisteki toplanti salonunun aylik kirasi ne kadar?

**Degerlendirme:** dogru sekilde reddetti

**Yanit:**

```
Bilgilendirilen bilgilerde, toplanti odalari, toplanti odalari ve toplanti notu gibi bilginin tüm alanlarında bilinen bilgi bulunmuyor. Bu da bunu ve diğer bilgilere göre
```

### T03 - KALDI

**Soru:** Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Bu bilgilendirme sistemi genellikle bu bilgiyi ayırt edebilir ve bu bilgiyi kullanmak için bu bilgilendirme sistemi kullanmak gereklidir. B
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
