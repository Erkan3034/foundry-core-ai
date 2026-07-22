# Yanit Kalitesi Degerlendirme Sonuclari

Calistirma: 2026-07-22 08:24

Bu rapor `python eval/run_eval.py` ile uretilir. Unit testlerden farki:
kodun calistigini degil, asistanin **dogru cevap verdigini** olcer.

## Ozet

- Toplam soru: **23**
- Gecti: **15** / 19 otomatik puanlanan (%79)
- Kaldi: **4**
- Manuel inceleme: 4
- Medyan yanit suresi: **16.26 s**
- En yavas yanit: 74.09 s

### Kategori bazinda

| Kategori | Gecti / Toplam | Ne olcuyor |
|---|---|---|
| cevaplanabilir | 12 / 12 | Belgedeki bilgiyi bulup dogru kaynakla veriyor mu |
| cevaplanamaz | 3 / 4 | Belgede olmayan bilgiyi uydurmuyor mu |
| tuzak | 0 / 3 | Anahtar kelime eslesiyor ama cevap yok - yine de reddediyor mu |
| kenar_durum | 0 / 4 | Bozuk/asiri genel girdide cokmuyor mu |

## Soru bazinda sonuclar

| ID | Tip | Soru | Durum | Kaynak | Parca | Guven | Sure |
|---|---|---|---|---|---|---|---|
| C01 | cevaplanabilir | Ise yeni baslayan bir calisan ilk yilini doldurunca kac is gunu yillik izne hak kazanir? | **GECTI** | izin_politikasi.txt, ise_alim_oryantasyon.txt | 3 | 0.655 | 17.02s |
| C02 | cevaplanabilir | Izin talebi en az kac is gunu once girilmelidir? | **GECTI** | izin_politikasi.txt, vpn_ve_bt_sss.txt | 3 | 0.504 | 17.20s |
| C03 | cevaplanabilir | Evlilik durumunda kac is gunu ucretli mazeret izni verilir? | **GECTI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.612 | 14.57s |
| C04 | cevaplanabilir | Sehir ici is yemeklerinde kisi basi ust limit nedir? | **GECTI** | seyahat_politikasi.txt, masraf_politikasi.txt | 3 | 0.507 | 71.12s |
| C05 | cevaplanabilir | Musteri agirlama yemeklerinde kisi basi limit ne kadardir? | **GECTI** | masraf_politikasi.txt, seyahat_politikasi.txt | 3 | 0.485 | 14.48s |
| C06 | cevaplanabilir | Gecikmis masraf talepleri kac gun sonra odenmez? | **GECTI** | masraf_politikasi.txt, izin_politikasi.txt | 3 | 0.418 | 15.84s |
| C07 | cevaplanabilir | Haftada en fazla kac gun uzaktan calisabilirim? | **GECTI** | uzaktan_calisma.txt, politika.txt, toplanti_ve_ofis_kurallari.txt | 3 | 0.445 | 15.75s |
| C08 | cevaplanabilir | Hangi gun tum ekiplerin ofiste bulunmasi zorunludur? | **GECTI** | toplanti_ve_ofis_kurallari.txt, uzaktan_calisma.txt, etik_ve_uyum.txt | 3 | 0.429 | 16.26s |
| C09 | cevaplanabilir | Standart mesai saatleri nedir? | **GECTI** | uzaktan_calisma.txt, seyahat_politikasi.txt, yan_haklar.txt | 3 | 0.335 | 17.05s |
| C10 | cevaplanabilir | Kurumsal VPN istemcisinin adi nedir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, bilgi_guvenligi.txt | 3 | 0.488 | 15.35s |
| C11 | cevaplanabilir | VPN baglantisi kac saat sonra otomatik olarak sonlanir? | **GECTI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt | 3 | 0.562 | 16.94s |
| C12 | cevaplanabilir | Standart dizustu bilgisayar yenileme suresi kac yildir? | **GECTI** | vpn_ve_bt_sss.txt, ise_alim_oryantasyon.txt | 3 | 0.597 | 16.11s |
| R01 | cevaplanamaz | Sirketin 2025 yili cirosu ne kadardir? | **GECTI** | izin_politikasi.txt, yan_haklar.txt | 3 | 0.304 | 16.67s |
| R02 | cevaplanamaz | Sirketin Paris ofisinin adresi nedir? | **GECTI** | politika.txt | 1 | 0.349 | 6.91s |
| R03 | cevaplanamaz | Calisanlara hisse senedi opsiyonu veriliyor mu? | **GECTI** | bilgi_guvenligi.txt, yan_haklar.txt, masraf_politikasi.txt | 3 | 0.322 | 14.32s |
| R04 | cevaplanamaz | Sirketin CEO'su kimdir ve sirket hangi yil kurulmustur? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt, izin_politikasi.txt | 3 | 0.281 | 17.60s |
| T01 | tuzak | Yillik ciro hedefi ve kar marji nedir? | **KALDI** | izin_politikasi.txt, performans_degerlendirme.txt, masraf_politikasi.txt | 3 | 0.329 | 74.09s |
| T02 | tuzak | Ofisteki toplanti salonunun aylik kirasi ne kadar? | **KALDI** | toplanti_ve_ofis_kurallari.txt, yan_haklar.txt | 3 | 0.482 | 33.36s |
| T03 | tuzak | Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar? | **KALDI** | vpn_ve_bt_sss.txt, uzaktan_calisma.txt | 3 | 0.507 | 19.40s |
| K01 | kenar_durum | _(bos)_ | **INCELE** | - | 0 | 0.000 | 0.00s |
| K02 | kenar_durum | ? | **INCELE** | - | 0 | 0.000 | 3.60s |
| K03 | kenar_durum | merhaba | **INCELE** | izin_politikasi.txt, ise_alim_oryantasyon.txt | 3 | 0.366 | 18.21s |
| K04 | kenar_durum | Sirket hakkindaki her seyi bana tek tek anlat | **INCELE** | politika.txt, bilgi_guvenligi.txt, ise_alim_oryantasyon.txt | 3 | 0.374 | 15.10s |

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

### C04 - GECTI

**Soru:** Sehir ici is yemeklerinde kisi basi ust limit nedir?

**Degerlendirme:** icerik + kaynak dogru

**Yanit:**

```
1. Yalnizca BAGLAM'daki gercekleri kullan. BAGLAM'da GECMEYEN sayi, tutar, tarih,
   yuzde veya isim URETME.

2. Kullanicinin sordugu dilde (Turkce soruya Turkce, Ingilizce soruya Ingilizce)
   kisa ve net yaz.

BAGLAM:
[KAYNAK: seyahat_politikasi.txt | PARCA 1]
secilir. Sehir bazli gecelik konaklama limitleri portalda yayinlanir; Istanbul, Ankara ve Izmir icin standart limit gecelik 4.500 TL'dir. Limit ustu konaklamalar direktor onayi gerektirir.
Gunluk Harcirah
Yurt ici seyahatlerde gunluk harcirah 1.200 TL, yurt disi seyahatlerde ulke grubuna gore 60 - 100 EUR'dur. Harcirah, yemek ve sehir ici kucuk ulasim giderlerini kapsar; ayrica fisli yemek masrafi talep edilemez.

Seyahat Guvenligi
Yurt disi seyahatlerden once seyahat saglik sigortasi otomatik olarak duzenlenir. Riskli bolgelere seyahat, Guvenlik ekibinin on degerlendirmesine tabidir. Acil durumlarda 7/24 seyahat destek hatti +90 212 000 00 00 aranmalidir.

---

[KAYNAK: masraf_politikasi.txt | PARCA 2]
MASRAF VE HARCAMA POLITIKASI

Genel Ilkeler
Is amacli yapilan harcamalar, belgelendirilmek kosuluyla sirket tarafindan karsilanir. Tum masraf kayitlari, harcamayi takip eden 10 is gunu icinde masraf yonetim sistemine fis veya fatura goruntusu ile girilmelidir. 30 gunu asan gecikmis masraf talepleri odenmez.

Yemek Masraflari
Sehir ici is yemeklerinde kisi basi ust limit 750 TL'dir. Musteri agirlama yemeklerinde limit kisi basi 1.500 TL'dir ve yonetici on onayi gerekir. Alkollu icecek masraflari sirket tarafindan karsilanmaz.

Ulasim Masraflari
Sehir ici is seyahatlerinde oncelikle toplu tasima veya kurumsal anlasmali taksi uygulaması kullanilır. Ozel arac kullaniminda kilometre basina yakit bedeli, her yil Ocak ayinda guncellenen kurumsal tarife uzerinden odenir. Havalimani transferlerinde standart taksi ucreti karsilanir.

---

[KAYNAK: seyahat
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
OTOMATİK SONLANMA SAATI: 12 SADARCI SANIYE AKTSI.
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
Üzgünüz, bu bilgilerimizle ilgili bilgim yoktur. Ancak, şirketin kuruluş tarihi ve CEO'nun kim olduğunu öğrenmek için daha fazlasını aramak gerekir. Bu bilgilerinizi nasıl paylaşabilirsiniz?
```

### T01 - KALDI

**Soru:** Yillik ciro hedefi ve kar marji nedir?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Kar Marji: Yillik Ciro Hedefi

- **Hedef**: Birçok iş için gereken ciro ve tedavilerin bir örneği olan yillik ciro hedefi, bir kişinin yıldızlık veya bir iş için gereklenecek ciro miktarını gösterir.

- **Kar Marji**: Kar Marji, bir kişinin yıldızlık veya bir iş için gereklenecek ciro miktarını gösterir.

- **Hedef Miktarı**: Yillik ciro hedef
```

### T02 - KALDI

**Soru:** Ofisteki toplanti salonunun aylik kirasi ne kadar?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Aylik toplanti salonunun kirasi, sirket tarafından belirlenen ve toplanti salonuna kazandırmak için kullanılan bir maliyettır. Bu maliyet,
```

### T03 - KALDI

**Soru:** Kurumsal VPN altyapisinin yillik maliyeti butcede ne kadar?

**Degerlendirme:** UYDURDU - belgede olmayan bilgiye cevap uretti

**Yanit:**

```
Bu bilginizin kesin tanımı bulunmadığı için, doğru bir hesaplayıcı çıkarma işlemi gerçekleştirebilmemiş olabilirim. Ancak, genellikle bu tip bir şeyin yıllık maliyeti yaklaşık 500 TL ila 1000 TL arasında düşünebilir. Bu miktarın kesin değerini kesin bir hesaplayıcıya göre bulmanız önerilir.
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
