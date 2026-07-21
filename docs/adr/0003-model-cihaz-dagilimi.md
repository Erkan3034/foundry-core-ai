# ADR-0003: Embedding modeli CPU'da, chat modeli GPU'da

**Durum:** Kabul edildi
**Tarih:** 2026-07-21

## Baglam

Foundry Local, modelleri varsayilan olarak mevcut en hizli donanima (`auto`)
yerlestirir. Hedef gelistirme makinesinde 2 GB VRAM'li bir GPU var
(GeForce MX450).

Her iki model de `auto` birakildiginda embedding modeli ve chat modeli ayni
anda GPU'ya yerlesmeye calisiyor ve VRAM'e sigmiyor. Bellek tasmasi yalnizca
yavaslamaya degil, **bozuk ciktiya** da yol aciyor.

## Karar

Varsayilan yapilandirmada:

- `EMBEDDING_DEVICE=generic-cpu` - embedding modeli CPU'da calisir
- `CHAT_DEVICE=auto` - chat modeli mevcut hizlandiriciya yerlesir

## Gerekce

Iki modelden hangisinin GPU'da olmasi gerektigi, is yukunun sekline gore
belirlendi:

- **Embedding** kisa metinler uzerinde calisir ve sonuclari kalicidir; bir
  parca bir kez embed edilir, sonra veritabaninda durur. Sorgu tarafinda tek
  bir kisa metin embed edilir. CPU'da kabul edilebilir.
- **Chat uretimi** her sorguda token-token calisir ve kullanicinin bekledigi
  gecikmenin tamamini olusturur. Hizlandirmadan en cok fayda goren asama budur.

## Sonuclar

- Sorgu basina embedding maliyeti CPU'ya kaydigi icin bir miktar arti gecikme
  var; ancak toplam gecikmenin baskin bileseni token uretimi oldugu icin net
  etki pozitif.
- **Ingestion belirgin sekilde yavasladi** (yuzlerce parcanin embedding'i
  CPU'da uretiliyor). Ingestion tek seferlik/arka plan islemi oldugu icin bu
  takas kabul edildi.
- 8 GB+ VRAM'li bir makinede her iki degisken de `auto` yapilabilir. Bu
  karar donanima bagli bir varsayilandir, mimari bir zorunluluk degildir.
