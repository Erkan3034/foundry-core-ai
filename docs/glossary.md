# Terim Sozlugu

Bu projede gecen terimlerin ortak tanimlari. Amac: kodda, dokumanda ve sunumda
ayni kavram icin ayni kelimenin kullanilmasi.

## Temel akis

| Terim | Tanim |
|---|---|
| **RAG** (Retrieval-Augmented Generation) | Modelin kendi ezberi yerine, once ilgili belge parcalarini **bulup** (retrieve) bunlari promptun icine **ekleyip** (augment) sonra yanit **urettigi** (generate) tasarim deseni. Amac: uydurmayi azaltmak, kaynak gosterebilmek. |
| **Bilgi tabani** (knowledge base) | Asistanin cevap uretirken kullanabilecegi tum belgelerin ve bunlardan cikarilmis parcalarin saklandigi yer. Bu projede tek bir SQLite dosyasi (`knowledge_base.db`). |
| **Ingestion** (belge alimi) | Bir belgeyi okuyup metne cevirme, parcalara bolme, her parcanin embedding'ini uretme ve veritabanina yazma islemi. Sorgu aninda degil, belge eklendiginde bir kez calisir. |
| **Parca** (chunk) | Bir belgenin, tek basina anlamli olacak buyuklukte kesilmis bolumu. Retrieval'in calisma birimi belge degil, parcadir. |
| **Baglam** (context) | Bulunan parcalarin birlestirilip sistem promptuna yerlestirilen hali. Modelin "sadece buna bakarak cevapla" dedigi metin. |
| **Kaynak** (source) | Bir parcanin geldigi belgenin adi. Yanitin sonunda `[Kaynak: dosya_adi]` olarak gosterilir; kullanicinin cevabi dogrulayabilmesini saglar. |
| **Uydurma** (hallucination) | Modelin baglamda olmayan bir bilgiyi, sanki belgede varmis gibi uretmesi. RAG'in engellemeye calistigi temel hata. `eval/questions.json` icindeki `cevaplanamaz` ve `tuzak` sorulari bunu olcer. |

## Arama

| Terim | Tanim |
|---|---|
| **Embedding** | Bir metnin anlamini temsil eden sayi vektoru. Anlamca benzer metinler, vektor uzayinda birbirine yakin dusER. |
| **Kosinus benzerligi** | Iki vektor arasindaki aciyi olcen, 0-1 arasi benzerlik skoru. 1'e yakin = anlamca cok benzer. |
| **Dense arama** | Embedding vektorleri uzerinden yapilan anlamsal arama. Kelimeler farkli olsa da anlam yakinsa bulur. |
| **Sparse arama / BM25** | Kelime eslesmesine dayali klasik arama. Anlami bilmez ama kullanicinin yazdigi terimin tam olarak gectigi yeri bulur. |
| **Hibrit arama** | Dense ve sparse ayaklarin birlikte kullanilmasi. Bkz. [ADR-0002](adr/0002-hibrit-arama.md). |
| **RRF** (Reciprocal Rank Fusion) | Iki farkli arama sonucunu, skorlarini degil **siralamalarini** kullanarak birlestiren yontem. Skorlar farkli olceklerde oldugu icin tercih edildi. |
| **`TOP_K_RETRIEVAL`** | Modele kac parca gonderilecegi. Az olursa cevap eksik kalir, cok olursa baglam kirlenir ve yavaslar. |
| **`MIN_SIMILARITY`** (benzerlik esigi) | Bu skorun altindaki parcalar alakasiz sayilir ve atilir. Hicbir parca esigi gecemezse LLM **hic cagrilmaz**, dogrudan "belgelerde bilgi yok" donulur - bu hem hiz hem dogruluk kazancidir. |
| **Keyword rescue** | Anahtar kelimesi eslesen parcalar icin benzerlik esiginin bir miktar gevsetilmesi (`KEYWORD_RESCUE_RATIO`). Esik **sifirlanmaz**; yoksa kelimenin gectigi her belge alakasiz sorulara cevap olurdu. |
| **Vektor onbellegi** | Tum embedding'lerin RAM'de tek bir NumPy matrisinde tutulmasi. Belge eklenince/silininde gecersiz kilinmasi zorunludur. Bkz. [ADR-0004](adr/0004-vektor-deposu-sqlite.md). |

## Model ve uretim

| Terim | Tanim |
|---|---|
| **Foundry Local** | Microsoft'un, dil modellerini tamamen cihaz uzerinde calistiran calisma zamani ve SDK'si. Model indirmeyi, donanim hizlandirmayi ve cikarimi yonetir; bulut hesabi gerektirmez. |
| **Model alias** | Bir modelin insan tarafindan okunabilir adi (or. `qwen2.5-1.5b`). Foundry Local bunu donanima uygun bir **varyanta** cozer. |
| **Varyant** (variant) | Ayni modelin belirli bir donanim icin derlenmis hali (or. `generic-cpu`, `cuda-gpu`). Bkz. [ADR-0003](adr/0003-model-cihaz-dagilimi.md). |
| **Instruct model** | Talimat takip etmek uzere egitilmis model. **Reasoning modelinin** aksine yanittan once `<think>` blogu uretmez. Bkz. [ADR-0001](adr/0001-chat-modeli-secimi.md). |
| **Token** | Modelin isledigi en kucuk metin birimi; kabaca bir kelime parcasi. |
| **`MAX_TOKENS`** | Yanitin ust uzunluk siniri. Reasoning modellerde bu butce `<think>` blogunda tukenip bos yanita yol acabilir. |
| **`TEMPERATURE`** | Ornekleme rastgeleligi. Dusuk = daha kararli ve tekrarlanabilir; kurumsal soru-cevapta dusuk tutulur. |
| **`FREQUENCY_PENALTY`** | Tekrarlayan token'lari cezalandiran ornekleme parametresi. Bu projede kapali; tekrar donguleri deterministik tespitle kesiliyor. Bkz. [ADR-0007](adr/0007-tekrar-dongusu-savunmasi.md). |
| **Streaming / SSE** | Yanitin tamamlanmasini beklemeden token token gonderilmesi (Server-Sent Events). Algilanan gecikmeyi belirgin sekilde dusurur. |
| **TTFT** (Time To First Token) | Ilk token'in ekrana dusmesine kadar gecen sure. Streaming'de kullanicinin gercekten hissettigi gecikme budur. |
| **TPS** (Tokens Per Second) | Saniyede uretilen token sayisi; uretim hizinin olcusu. |

## Erisim ve guvenlik

| Terim | Tanim |
|---|---|
| **Rol** | `admin` veya `user`. Belge yukleme/silme ve sifirlama yalnizca `admin`; soru sorma her giris yapmis kullaniciya acik. |
| **Oturum token'i** | Girise karsilik uretilen rastgele dize. Sunucu tarafinda saklanir (JWT degil), boylece cikis aninda gercekten gecersizlesir. |
| **KDF / scrypt** | Parolayi hash'lemek icin kullanilan, **kasitli olarak yavas ve bellek-yogun** fonksiyon. Amac, calinan bir veritabaninda parolalarin kaba kuvvetle kirilmasini pahali hale getirmek. |
| **Salt** | Her parola hash'ine eklenen rastgele deger. Ayni parolaya sahip iki kullanicinin ayni hash'i uretmesini engeller. |
| **Denetim kaydi** (audit log) | Kim, ne zaman, hangi yonetimsel islemi yapti kaydi. |
