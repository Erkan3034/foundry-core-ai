# ADR-0006: Ag erisimi ve tasima guvenligi

**Durum:** Kabul edildi (dagitim onkosuluyla)
**Tarih:** 2026-07-21

## Baglam

Projenin temel iddiasi: veriler cihazdan cikmaz, internet gerekmez.

`API_HOST` varsayilani `127.0.0.1`. Bu degerde iddia kosulsuz dogrudur; servise
yalnizca ayni makineden erisilebilir.

Gelistirme sirasinda arayuzun mobil gorunumu test edilirken `API_HOST=0.0.0.0`
kullanildi ve servise yerel agdaki baska cihazlardan erisildi. Bu, uygulamayi
duz HTTP uzerinden aga acar. [ADR-0005](0005-kimlik-dogrulama.md) ile eklenen
parola tabanli kimlik dogrulama, tasima sifrelemesi olmadan **agi dinleyen
birine karsi koruma saglamaz**: parolalar ve oturum token'lari acik metin gider.

## Karar

- Varsayilan `API_HOST=127.0.0.1` olarak kalir. `.env.example` bu degeri tasir.
- `0.0.0.0` bilincli bir dagitim karari olarak degerlendirilir ve **onunde TLS
  sonlandiran bir ters vekil (nginx / Caddy / IIS) bulunmasi kosuluyla**
  kabul edilir.
- Uygulama kendi basina TLS sonlandirmaz. Sertifika yonetimi ve yenileme,
  uygulamanin degil dagitim katmaninin sorumlulugudur.

## Gerekce

Uygulama icine TLS gomulmesi sertifika uretimi, saklanmasi ve yenilenmesi
sorunlarini uygulamaya tasirdi. Bu, tek dosyalik / kurulumsuz calisma
iddiasiyla celisir. Ters vekil, cozulmus bir problemi cozulmus haliyle
kullanmayi saglar.

## Sonuclar

- **Yerel kullanim (varsayilan):** cevrimdisi iddiasi kosulsuz gecerli.
- **Ag uzerinden kullanim:** cevrimdisi iddiasi "internete cikmaz" olarak
  gecerli kalir, ancak "veri cihazdan cikmaz" iddiasi artik "veri yerel agdan
  cikmaz" seklinde daraltilmali. Bu ayrim README'de acikca yazilmalidir.
- Ters vekil olmadan `0.0.0.0` ile calistirmak **desteklenmeyen bir
  yapilandirmadir**. Gelistirme sirasinda bilerek yapildiysa, dagitimdan once
  geri alinmalidir.

## Acik is

- [x] Uygulama acilisinda `API_HOST` 127.0.0.1 disinda ise loglara belirgin bir
      uyari basilmasi — `api_server.py` lifespan icinde mevcut.
