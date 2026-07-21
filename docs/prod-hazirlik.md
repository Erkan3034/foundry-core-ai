# Prod-Hazirlik Denetimi

**Tarih:** 2026-07-21 · Tum sayilar bu makinede (GeForce MX450, 2 GB VRAM,
embedding CPU'da) bos sistemde olculmustur ve tekrarlanabilir cikmistir
(iki bagimsiz kosuda ayni kategori sonuclari).

## Olculen durum

| Olcum | Sonuc | Kaynak |
|---|---|---|
| Birim/entegrasyon testleri | **159/159 gecti** (23 sn) | `pytest tests/` |
| Yanit kalitesi (genel) | **%74** (14/19 otomatik puanlanan) | `eval/RESULTS.md` |
| — cevaplanabilir sorular | 11/12 | " |
| — cevaplanamaz (reddetme) | 3/4 | " |
| — tuzak sorular | **0/3** | " |
| Vektor arama | 0.047 ms/sorgu (21.300 QPS) | `benchmark.py` |
| Uretim hizi | 19 token/sn | " |
| Ilk token suresi (TTFT) | **15.4 sn** | " |
| Medyan toplam yanit | 15.5 sn | `eval/RESULTS.md` |

## Guclu yanlar (denetimde dogrulandi)

- Parola guvenligi ciddi is: scrypt + rastgele salt + sabit zamanli
  karsilastirma + kullanici-yok durumunda sahte hash dogrulamasi (kullanici
  adi sizdirmaz) + oturum token'lari **hash'lenerek** saklaniyor (`auth.db`
  calinsa bile oturumlar tekrar oynatilamaz).
- Ilk admin rastgele parolayla dogar; sabit "admin/admin" yok.
- `API_HOST=0.0.0.0` acilista loglara uyari basiyor.
- Bos sorgu, alakasiz sorgu ve model dongusu senaryolari coktumuyor
  (eval `kenar_durum` ve iki kosuda sahada tetiklenen dongu kesici).
- Kurulum betigi son adimda 159 testi kosarak kendini dogruluyor.

## Zayifliklar ve kapatma yollari (onem sirasiyla)

### Z1 — Tuzak sorularda uydurma (0/3) · en kritik
Getirilen parca konuyla ilgili ama cevabi icermiyorsa model boslugu dolduruyor.
**Kok neden teshis edildi:** keyword-rescue, BM25 *siralamasina* degil salt
eslesme listesine bakiyor; "sirket", "yillik", "hangi" gibi her belgede gecen
kelimeler, benzerligi esik altindaki parcalari kurtarip LLM'e tasiyor
(R04 guven=0.281 < esik=0.35, yine de 3 parca gitti).
**Kapatma:** (1) rescue'yu BM25'in ilk N sonucuyla sinirla, (2) soru kelimeleri
icin Turkce stopword listesi (`search_text.py`), (3) uretilen sayilarin
baglamda gectigini dogrulayan cikti kontrolu, (4) firma donaniminda daha buyuk
model (`phi-4-mini`). (1)+(2) birkac satirlik is; ancak retrieval'i degistirdigi
icin **ayri dogrulama setiyle kalibrasyon** sarttir (bkz. `eval/README.md`) -
23 soruya gore ayar yapmak ezberletmek olur.

### Z2 — TTFT 15.4 sn (plan hedefi 1-3 sn idi)
Uretim 1 sn; zamanin tamami oncesinde: CPU'daki sorgu embedding'i + 4000
karakterlik baglamin prefill'i.
**Kapatma:** firma donaniminda (6+ GB VRAM) `EMBEDDING_DEVICE=auto` yapmak en
buyuk kazanc; ikincisi `MAX_CONTEXT_LENGTH`/`TOP_K` dusurmek (kalite etkisi
eval ile olculerek). Streaming sayesinde algi kismen yonetiliyor ama 15 sn
"dusunuyor" ekrani prod'da sikayete doner. Donanim onerisi `docs/dagitim.md`'de.

### Z3 — Login'de kaba kuvvet kilidi yok
scrypt maliyeti (~60ms/deneme) tek fren; LAN'daki biri sinirsiz deneyebilir.
Denemeler denetim kaydina dusuyor ama otomatik engel yok.
**Kapatma:** kullanici basina N basarisiz denemede artan gecikme / gecici
kilit (`auth.authenticate` tek nokta, ~30 satir). TLS vekil onerisi zaten
ADR-0006'da.

### Z4 — Dongu kesici uretimden SONRA calisiyor
T01'de model 1024 token'lik butceyi dongude yakti (72 sn), kesici cikti
metnini temizledi ama sureyi kurtaramadi.
**Kapatma:** uretim sirasinda durdurma (streaming yolunda kesici zaten uretimi
kesiyor; streaming olmayan yol icin SDK'nin durdurma kriterleri arastirilacak).
ADR-0007'de acik is olarak kayitli.

### Z5 — Yakin sayisal degerlerde karisiklik (C04)
"Sehir ici yemek limiti" sorusuna ayni cumledeki iki rakamdan yanlisini
(750 yerine 1.500) veriyor; uc kosuda da ayni hata.
**Kapatma:** model kapasitesi siniri - firma donaniminda buyuk model; veya
Z1'deki cikti dogrulamasi bunu da yakalar (1.500 baglamda var ama yanlis
baglamda - tam cozum degil, dokumante edilmis sinir).

### Z6 — Eval seti kucuk (23 soru) ve ayni zamanda ayar seti
Her kalibrasyon bu sete ezberleme riski tasiyor.
**Kapatma:** firma pilotunda gercek kullanici sorularindan ayri bir dogrulama
seti toplamak; ilk musteri teslimatinin dogal ciktisi.

### Z7 — CI kostu ve GERCEK bir tasinabilirlik hatasi yakaladi ✅ kapandi
Ilk kosuda 10 test modulu `ModuleNotFoundError` ile toplanamadi.
**Kok neden:** testler `from config import CONFIG` gibi duz import kullaniyor;
bu yalnizca proje koku `sys.path`'te ise calisir. Gelistirme boyunca hep
`python -m pytest` kullanildi - bu bicim calisma dizinini `sys.path`'e ekleyip
sorunu **gizliyordu**. CI ise normal `pytest` komutunu kullandi ve gizlenen
hata ortaya cikti.

Etkisi CI ile sinirli degildi: depoyu klonlayip `pytest` yazan **her
gelistirici** ve kodu inceleyen her firma ayni 10 hatayi alirdi. "159 test
geciyor" iddiasi tek bir cagirma bicimine bagliymis.

**Cozum:** `pytest.ini` icinde `pythonpath = .`. Uc bicimde de (`pytest`,
`pytest tests/`, `python -m pytest`) 159/159 dogrulandi.

**Yan bulgu (olumlu):** Ayni kosu, `foundry-local-sdk`'nin temiz bir Windows
runner'inda `pip install -r requirements.txt` ile sorunsuz kuruldugunu
kanitladi - onceki commit'te eklenen eksik bagimlilik duzeltmesi dogrulandi.

### Z8 — Suresi dolan oturum satirlari silinmiyor (dusuk)
`auth.db` cok yavas buyur. Acilista tek `DELETE ... WHERE expires_at < now`
yeterli.

## Karar: hangi senaryoda prod-ready?

**EVET** — 5-10 kisilik birim; Windows makine; localhost veya TLS vekil
arkasinda; ic politika/SSS gibi "yanlis cevabin maliyeti dusuk, kaynak linki
ile dogrulanabilir" iceriklerde. Kaynak gosterme + reddetme davranisi +
denetim kaydi bu senaryo icin yeterli olgunlukta.

**HENUZ DEGIL** — yuzlerce es zamanli kullanici (tek islem/kilit); Linux
sunucu (calisma zamani yok, ADR-0008); hukuki/tibbi/finansal gibi yanlis
cevabin maliyetli oldugu alanlar (Z1 kapanmadan olmaz).

## Dagitim ozeti

Tek adim: `install.ps1 -PreloadModels` (dogrulamali, idempotent) +
`start.bat` + `requirements.lock` (sabit surumler). Docker bilerek yok:
Foundry Local'in Linux calisma zamani bulunmuyor - gerekce ve yeniden acma
kosulu [ADR-0008](adr/0008-dagitim-stratejisi.md)'de. Firma rehberi:
[docs/dagitim.md](dagitim.md).
