# Firma Teslim Rehberi

Bu dokuman, Foundry Core AI'nin farklı bir  makineye kurulumunu, guvenli
yapilandirmasini ve isletimini anlatir. Neden Docker kullanilmadigi:
[ADR-0008](adr/0008-dagitim-stratejisi.md).

## Sistem gereksinimleri

| | Asgari | Onerilen |
|---|---|---|
| Isletim sistemi | Windows 10 22H2 | Windows 11 |
| RAM | 8 GB | 16 GB |
| Disk | 15 GB bos alan | SSD |
| GPU | Gerekmez (CPU'da calisir) | 6+ GB VRAM (yanit suresini dusurur) |
| Ag | Yalnizca **kurulumda** internet | Kurulum sonrasi tamamen cevrimdisi |

## Kurulum (tek adim)

Proje klasorunu hedef makineye kopyalayin (veya `git clone`), sonra:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -PreloadModels
```

Betik sirasiyla: Python 3.11+ ve Foundry Local'i dogrular (yoksa winget ile
kurar), sanal ortami kurar, bagimliliklari `requirements.lock`'tan sabit
surumlerle yukler, `.env` olusturur, **166 birim testini calistirarak kurulumu
dogrular** ve `-PreloadModels` verildiyse modelleri (~2-3 GB) indirir.

Testler gectiyse kurulum saglamdir. Gunluk baslatma: `start.bat`
(veya hizmet olarak kosturmak icin asagiya bakin).

## Ilk acilis

1. `start.bat` calistirin; arayuz `http://localhost:8000`.
2. Ilk aciliste `admin` hesabi **rastgele parolayla** olusturulur ve parola
   konsola yazilir. Kaydedin, ilk giriste degistirin. Sabit "admin/admin"
   parolasi bilerek yoktur ([ADR-0005](adr/0005-kimlik-dogrulama.md)).
3. Belgeleri `documents\` klasorune koyun ve calistirin:
   `venv\Scripts\python main.py ingest`
   (Arayuzden tek tek dosya yukleme de mumkun; toplu ilk yukleme icin komut
   daha hizli.) Ingestion CPU'da calisir; buyuk arsivlerde saatler surebilir,
   bir kereliktir.

## Guvenlik varsayilanlari

- Servis varsayilan olarak **yalnizca kurulu makineden** erisilir
  (`API_HOST=127.0.0.1`). Bu, "veri cihazdan cikmaz" garantisinin kendisidir.
- Birim icindeki baska bilgisayarlarin erismesi isteniyorsa `API_HOST=0.0.0.0`
  yapilabilir; ancak bu durumda **onune TLS sonlandiran bir ters vekil**
  (IIS/nginx/Caddy) konulmalidir. Duz HTTP'de parolalar agda acik gider.
  Ayrinti: [ADR-0006](adr/0006-ag-erisimi-ve-tasima-guvenligi.md).
- Roller: `admin` belge yukler/siler ve kullanici yonetir; `user` yalnizca
  soru sorar. Tum yonetimsel islemler denetim kaydina yazilir
  (`GET /auth/audit-log`).

## Yedekleme

Iki dosya yedeklenir, ikisi de SQLite'tir; kopyalamak yeterlidir:

| Dosya | Icerik | Kaybi ne demek |
|---|---|---|
| `knowledge_base.db` | Belgeler + embedding'ler | Yeniden ingestion gerekir (zaman kaybi, veri kaybi degil - kaynak belgeler durdukca) |
| `auth.db` | Hesaplar + denetim kaydi | Hesaplar ve kayit gecmisi gider |

Yedek almadan once servisi durdurun (Ctrl+C / pencereyi kapatin).

## Guncelleme

```powershell
git pull
powershell -ExecutionPolicy Bypass -File install.ps1
```

Betik idempotent'tir: var olan `venv` ve `.env` korunur, yalnizca degisen
bagimliliklar yuklenir ve testler yeniden kosulur.

## Windows hizmeti olarak calistirma (istege bagli)

Kullanici oturumu acik kalmadan calismasi isteniyorsa en basit yol Gorev
Zamanlayici'dir: "Bilgisayar baslatildiginda" tetikleyicili, `start.bat`'i
calistiran bir gorev olusturun ("Run whether user is logged on or not"
secili). NSSM gibi araclarla gercek hizmet kaydi da mumkundur; ikisi de
uygulamada degisiklik gerektirmez.

## Bilinen isletim sinirlari

- **Linux sunucuya kurulamaz.** Foundry Local'in Linux calisma zamani yok
  ([ADR-0008](adr/0008-dagitim-stratejisi.md)). Urun, sunucu ciftligi icin
  degil, birim ici tek makine icin tasarlanmistir.
- **Tek islem, tek model.** Ayni anda gelen sorgular sirayla islenir (uretim
  kilidi). 5-10 kisilik bir birim icin uygundur; yuzlerce es zamanli kullanici
  hedefleniyorsa bu urunun kapsami disidir.
- **Ilk yanit gecikmesi.** Dusuk donanimda ilk token 10-15 sn surebilir;
  streaming sayesinde yanit akarak gelir. Olcumler: `python benchmark.py`.
