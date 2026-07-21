# ADR-0008: Dagitim stratejisi - Docker yerine yerel kurulum betigi

**Durum:** Kabul edildi
**Tarih:** 2026-07-21

## Baglam

Urun firmalara teslim edilecek. Ilk akla gelen dagitim yontemi Docker'di:
tek imaj, her yerde ayni davranis, kolay guncelleme.

Ancak uygulamanin kalbi olan Foundry Local calisma zamani **isletim sistemine
yerel** dagitilir. Kurulu SDK'nin (1.2.3) icerigi incelendiginde tum cekirdek
kutuphanelerin yalnizca Windows DLL'i oldugu goruldu:

```
foundry_local_core/bin/Microsoft.AI.Foundry.Local.Core.dll
onnxruntime_core/bin/onnxruntime.dll
onnxruntime_genai_core/bin/onnxruntime-genai.dll
```

Linux `.so` esdegerleri yok. Microsoft'un deposundaki Linux destegi talebi de
hala acik bir tartisma ([Foundry-Local discussions #61](https://github.com/microsoft/Foundry-Local/discussions/61));
resmi Linux surumu yayinlanmis degil. Standart Docker konteynerleri Linux
tabanli oldugu icin **bu stack Docker'da calismaz**.

Ikinci engel donanim: urunun performansi GPU/NPU hizlandirmasina dayaniyor
(bkz. ADR-0003). Konteynerde GPU gecisi, tam da kacinmaya calistigimiz kurulum
karmasikligini geri getirir.

## Degerlendirilen secenekler

| Secenek | Neden reddedildi |
|---|---|
| Linux Docker imaji | Foundry Local'in Linux calisma zamani yok; imaj hic ayaga kalkmaz |
| Windows konteyneri | Firmalarda cok nadir kullanilir; imajlar buyuk; GPU gecisi sorunlu |
| Foundry Local'i cikarip llama.cpp/ONNX ile konteynerlesme | Teknik olarak mumkun ama baska bir urun olur: model yonetimi, donanim secimi ve Foundry entegrasyonu - projenin kimligi - kaybolur |
| **Yerel kurulum betigi (secilen)** | Platformun kendi dagitim modeliyle uyumlu; donanim hizlandirmasi dogrudan calisir |

## Karar

Dagitim, hedef makinede calisan **idempotent bir kurulum betigi** ile yapilir:

- `install.ps1` - Python ve Foundry Local'i dogrular (gerekirse winget ile
  kurar), sanal ortami olusturur, bagimliliklari **requirements.lock**'tan
  sabitlenmis surumlerle yukler, `.env` olusturur, birim testlerini calistirip
  kurulumu dogrular. `-PreloadModels` ile modeller kurulum sirasinda indirilir.
- `start.bat` - gunluk kullanim icin tek tikla baslatici.
- `requirements.lock` - `pip freeze` ciktisi; iki farkli makinede ayni surumler.

## Destekleyen bulgu

Bu karar calisilirken gercek bir dagitim hatasi bulundu: `requirements.txt`
icinde `foundry-local-sdk` **yoktu**. Gelistirme makinesinde elle kuruldugu
icin fark edilmemisti; temiz bir makinede `pip install -r requirements.txt`
sonrasi uygulama `ModuleNotFoundError` ile acilmayacakti. Kurulum betiginin
son adiminin test kosusu olmasi tam bu tur hatalari yakalamak icindir.

## Sonuclar

- Dagitim Windows-oncelikli. macOS icin Foundry Local brew ile kurulabilir ama
  betigimiz yok; Linux sunucuya dagitim **mumkun degil** (calisma zamani yok).
  Bu, urunun "cihaz ici AI" konumlanisiyla tutarli bir sinir: hedef, sunucu
  ciftligi degil, calisanin/birimin kendi makinesi.
- Microsoft Linux destegi yayinlarsa bu ADR yeniden acilmali; o gun Docker
  imaji uretmek dogru adim olur.
- Guncelleme akisi "git pull + install.ps1 yeniden calistir" kadar basit;
  betik idempotent oldugu icin var olan kurulumu bozmaz.
