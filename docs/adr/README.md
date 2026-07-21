# Mimari Karar Kayitlari (ADR)

Bu klasor, projede alinmis ve **geri alinmasi maliyetli** kararlari kaydeder.
Amac, "neden boyle yapilmis?" sorusunun kodu tersine muhendislik etmeden
cevaplanabilmesi.

Bir karar buraya girer eger: birden fazla makul secenek vardi, secim bir seyi
kaybettirdi (takas), ve degistirmek birden fazla dosyaya dokunmayi gerektirir.

| # | Karar | Ozet |
|---|---|---|
| [0001](0001-chat-modeli-secimi.md) | Chat modeli `qwen2.5-1.5b` | Reasoning modelleri `<think>` blogunda token butcesini tuketiyor; planin onerdigi 3-5B hedef donanima sigmiyor |
| [0002](0002-hibrit-arama.md) | Hibrit arama (dense + BM25, RRF) | Turkce'nin sondan eklemeli yapisi saf dense aramayi zayiflatiyor |
| [0003](0003-model-cihaz-dagilimi.md) | Embedding CPU'da, chat GPU'da | 2 GB VRAM'e iki model sigmiyor; hizlandirmadan en cok fayda goren asama token uretimi |
| [0004](0004-vektor-deposu-sqlite.md) | SQLite + NumPy + RAM onbellegi | Harici vektor DB'si "tek dosya, kurulumsuz, cevrimdisi" iddiasini bozardi |
| [0005](0005-kimlik-dogrulama.md) | Rol tabanli kimlik dogrulama | Plandan bilincli sapma; kurumsal belgelerde "kim yukleyebilir/silebilir" sorusu |
| [0006](0006-ag-erisimi-ve-tasima-guvenligi.md) | Varsayilan `127.0.0.1`, TLS ters vekile birakildi | Uygulama ici TLS, kurulumsuz calisma iddiasiyla celisirdi |
| [0007](0007-tekrar-dongusu-savunmasi.md) | Ornekleme yerine deterministik dongu tespiti | `FREQUENCY_PENALTY` ayari modele ozgu ve kirilgandi; tespit model-bagimsiz ve olculebilir |
