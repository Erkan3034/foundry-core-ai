# Nerede Zorlandık, Nerede Yanıldık, Ne Öğrendik

Bu belge, projenin yapay zekâ tarafındaki teknik bulgularını kaydeder. Her
iddia `eval/RESULTS.md` ve `benchmark.py` ölçümlerine dayanır; tahmin
yoktur. Amaç, bir sonraki RAG sistemini kuran kişinin (bizim de dahil)
aynı duvarlara tekrar toslamaması.

---

## 1. En büyük yanılgı: testler geçiyordu, sistem uyduruyordu

**Durum.** 155 birim testi yeşildi. Retrieval çalışıyor, embedding üretiliyor,
API doğru yanıt veriyor, veritabanı tutarlı. Proje "bitmiş" görünüyordu.

Sonra asistanın **cevaplarını** ölçen ayrı bir set yazdık. İlk sonuç:

| Kategori | Sonuç |
|---|---|
| Cevabı belgede olan sorular | 11 / 12 |
| Cevabı belgede **olmayan** sorular | **1 / 4** |
| Tuzak sorular | **0 / 3** |

Yani sistem, bilmediği şeylerin dörtte üçünde bilgi **uyduruyordu**. Örnekler
kurgu değil, ölçümden:

> **Soru:** Ofisteki toplantı salonunun aylık kirası ne kadar?
> **Yanıt:** "Aylık toplantı salonunun kirası, 2026 yılı için 240 TL'dir."

Belgelerde "kira" kelimesi yalnızca "araç kiralama" olarak geçiyor. Rakam da
yıl da tamamen uydurma — üstelik son derece inandırıcı biçimde.

> **Soru:** Şirketin 2025 yılı cirosu ne kadardır?
> **Yanıt:** "2025 yılı cirosu 14 işgünlüğü yıllık izne hak kazandırmaktadır."

İzin politikasındaki sayıyı ciro sorusuna yapıştırmış.

**Öğrenilen.** Yazılım mühendisliğinde "testler geçiyor" ile "sistem doğru
çalışıyor" büyük ölçüde aynı şeydir. **Yapay zekâ sistemlerinde değildir.**
Birim testi kodun sözleşmesini doğrular; modelin davranışını doğrulamaz.
Model davranışı ancak *ölçülerek* bilinir ve ölçülmediği sürece, sistemin en
tehlikeli hatası görünmez kalır. Bir RAG projesinde değerlendirme seti
opsiyonel bir ekstra değil, testlerle eşit ağırlıkta ikinci bir disiplindir.

---

## 2. Sistem promptunda kuralın *sırası* sonucu değiştiriyor

Uydurmanın kök nedeni beklediğimizden basit çıktı. Promptun ilk hali şuydu:

```
Sen kurumsal bir bilgi asistanısın. BAĞLAM bilgilerini kullanarak
kullanıcının sorusuna doğrudan ve net bir yanıt ver.

Kurallar:
1. Sadece BAĞLAM içindeki gerçekleri kullan.
2. Kullanıcının dilinde yaz.
3. [Kaynak: dosya_adı] ekle.
4. BAĞLAM'da bilgi yoksa "bilgi bulunmuyor" de.
```

İki yapısal sorun var. Prompt **"yanıt ver" emriyle başlıyor** — modele
varsayılan davranış olarak cevaplamayı öğretiyor. Ve reddetme kuralı
**dördüncü, son sırada**.

Kuralı en başa, ilk kontrol olarak taşıdık; "bağlam konuyla ilgili görünse
bile cevap orada yazmıyorsa reddet" ve "bağlamda geçmeyen sayı/tutar/tarih
üretme" ifadelerini açıkça ekledik. Tek değişiklik buydu:

| Kategori | Önce | Sonra |
|---|---|---|
| Cevaplanabilir | 11 / 12 | 11 / 12 |
| Cevaplanamaz | **1 / 4** | **3 / 4** |
| **Genel** | **%60** | **%74** |

**Öğrenilen.** 1.5B parametreli bir model talimatları eşit ağırlıkta
değerlendirmez; listenin sonundaki kısıtı, baştaki emrin altında ezer.
Büyük modeller bu tür sıralamaya karşı daha dayanıklıdır — küçük modelde
prompt **mimarisi** bir uygulama detayı değil, sistemin davranışını belirleyen
asıl kaldıraçtır.

Kritik ayrıntı: reddetme iyileşirken doğru cevaplarda **hiç kayıp olmadı**.
Aynı kazanç benzerlik eşiğini yükselterek elde edilseydi, doğru cevaplardan da
kaybederdik. Yani bu, bedava bir kazanç değil — *doğru yerden* yapılmış bir
müdahaleydi.

---

## 3. En zor bulgu: benzerlik skoru, cevaplanabilirliğin göstergesi değil

Kalan hatalar tek bir sınıfta toplandı ve bu, projenin en öğretici kısmı oldu.

Ölçülen benzerlik skorları:

**Doğru cevaplanan sorular:** 0.335, 0.418, 0.429, 0.445, 0.485, 0.488,
0.504, 0.507, 0.562, 0.597, 0.612, 0.655

**Uydurulan sorular:** 0.281, 0.304, 0.322, 0.329, 0.349, **0.482**

Şu satıra dikkat: "Ofisteki toplantı salonunun aylık kirası" sorusu **0.482**
benzerlikle parça getirdi. Bu skor, doğru cevaplanan soruların
**çoğundan yüksek**. Getirilen parça (`toplanti_ve_ofis_kurallari.txt`)
gerçekten konuyla ilgiliydi — içinde toplantı salonu vardı, kira yoktu.

Bu, iki **farklı** başarısızlık modu olduğunu gösteriyor:

| Mod | Belirti | Çözüm aracı |
|---|---|---|
| **A — Alakasız parça eşiği geçiyor** | Düşük benzerlik (0.28–0.33), yine de LLM'e gidiyor | Eşik / kalibrasyon |
| **B — İlgili ama yetersiz parça** | **Yüksek** benzerlik (0.48), model boşluğu dolduruyor | Eşik ÇÖZMEZ |

**Öğrenilen.** Mod B, RAG'in yapısal sınırıdır ve bir eşik değeriyle
kapatılamaz. Çünkü "bu parça soruyla **ilgili** mi" ile "bu parça sorunun
**cevabını içeriyor** mu" iki ayrı sorudur — kosinüs benzerliği yalnızca
birincisini ölçer. Eşiği 0.48'in üstüne çıkarmak Mod B'yi çözerdi, ama doğru
cevapların yarısını da elerdi.

Bu ayrımı görmeden RAG sistemi ayarlamaya çalışmak, eşik değerini sonsuza
kadar ileri geri oynatmak demektir. Mod B'nin gerçek araçları farklıdır:
üretilen sayıların bağlamda geçtiğini doğrulayan çıktı kontrolü, daha güçlü
bir model, veya cevaplanabilirliği ayrıca puanlayan ikinci bir aşama.

---

## 4. Türkçe, dense retrieval'ı kırıyor

Program planı saf dense retrieval tarif ediyordu: sorguyu embed et, kosinüs
benzerliğine göre en yakın K parçayı al. Türkçede bu yaklaşım tek başına
yetersiz kaldı.

Sebep dilin sondan eklemeli yapısı. "izin", "izinleri", "izne", "izinlerin"
farklı yüzey formlar; küçük bir embedding modelinde bu formlar arasındaki
benzerlik, konusu uzak ama yüzeyi yakın bir parçanın benzerliğinin altında
kalabiliyor. Kullanıcının tam olarak yazdığı terimi içeren parça ilk K'ye
giremiyor.

Çözüm iki ayaklı arama oldu: dense (anlam) + BM25 (kelime), **Reciprocal Rank
Fusion** ile birleştirme. RRF'i seçmemizin sebebi önemli: iki yöntemin skorları
farklı ölçeklerde (kosinüs 0–1 arası, BM25 sınırsız). Skorları toplamak ölçek
kalibrasyonu gerektirir ve kırılgandır; RRF yalnızca **sıralamaları** kullandığı
için bu sorundan bağımsızdır.

BM25 tarafında iki Türkçeye özgü ayrıntı çıktı:

**Ön-ek eşleşmesi, ucuz bir stemmer yerine geçiyor.** Ekler sona geldiği için
terimi 5 karaktere kırpıp `parol*` şeklinde aramak, "parola / parolalar /
parolamız" formlarını tek seferde yakalıyor. Tam bir morfolojik çözümleyici
kurmadan, sondan eklemeli dilin retrieval maliyetinin büyük kısmı böyle
karşılanıyor.

**Türkçe "ı" bir aksan değildir.** SQLite FTS5'in `unicode61 remove_diacritics`
seçeneği "ü→u", "ö→o" katlamasını yapar ama "ı" (U+0131) ayrı bir harftir ve
otomatik katlanmaz. Ayrıca Python'un `lower()` metodu "I" harfini "i" yapar —
Türkçede doğrusu "ı"dır. Bu yüzden normalizasyonu elle yazmak ve **önce
katlayıp sonra küçültmek** zorunda kaldık. Kurumsal belgeler çoğu zaman
Türkçe karaktersiz yazıldığı için ("GUVENLIGI") bu katlama olmadan anahtar
kelime araması hiç çalışmıyordu.

**Öğrenilen.** İngilizce üzerine kurulmuş RAG tarifleri Türkçeye doğrudan
taşınmıyor. Dilin morfolojisi, retrieval mimarisini değiştiren birinci
dereceden bir tasarım kısıtı.

---

## 5. Kurtarma mekanizmasının kendisi bir hata kaynağı olabilir

Hibrit aramaya, anahtar kelimesi eşleşen parçalar için eşiği gevşeten bir
"kurtarma" katmanı eklemiştik (`KEYWORD_RESCUE_RATIO = 0.75`). Mantık makuldü:
kullanıcının yazdığı terimi birebir içeren bir parça, benzerlik skoru biraz
düşük diye elenmemeli.

Değerlendirme bunun **uydurmanın ana kaynaklarından biri** olduğunu gösterdi.

Kök neden: kurtarma, BM25'in **sıralamasına** değil, salt eşleşme listesine
bakıyor. "şirket", "yıllık", "hangi" gibi neredeyse her belgede geçen kelimeler
eşleşme üretiyor ve eşiğin altındaki alakasız parçaları LLM'e taşıyor. Ölçüm:
"Şirketin CEO'su kimdir" sorusu 0.281 benzerlikle (eşik 0.35) yine de 3 parça
getirdi.

**Öğrenilen.** Recall'ı artırmak için eklenen her mekanizma, precision'dan
sessizce ödün alır. Bu ödünün büyüklüğü ancak ölçülerek görülür — mekanizmayı
tasarlarken "makul" görünmesi hiçbir şey ifade etmiyor. Kendi yazdığımız kod
yorumu bu riski önceden not etmişti bile ("kelime eşleşmesi tek başına yeterli
değildir"); yine de ölçmeden önce ne kadar zarar verdiğini bilmiyorduk.

---

## 6. Ölçüm disiplini: kendi setine ezberletmemek

Ölçümler, `MIN_SIMILARITY` değerini 0.35'ten ~0.40'a çıkarmanın kalan
hataların bir kısmını çözeceğini açıkça gösteriyordu. Bunu **bilerek
yapmadık.**

Sebebi: elimizde 23 soru var. Hepsini eşik ayarlamak için kullanırsak, elde
edilen eşik bu 23 soruya *ezberlenmiş* olur ve "sistem iyileşti" iddiası
ölçülemez hale gelir. Doğru yöntem ayarlama seti ile doğrulama setini
ayırmaktır; ikinci set henüz yok.

Sunumdan önce sayıları güzelleştirmek için eşik oynatmak, ölçümün kendisini
anlamsız kılardı.

**Öğrenilen.** Bu klasik train/validation ayrımıdır ve model eğitmediğimiz,
yalnızca birkaç hiperparametre seçtiğimiz durumda bile geçerlidir. Bir
sistemi kendi test setine göre ayarlamak, iyileştirme değil kendini kandırmadır.

---

## 7. Model seçiminde "daha akıllı" her zaman daha iyi değil

Plan 3–5B parametreli bir model öneriyordu. Denemelerde iki ayrı tuzak çıktı.

**Reasoning modelleri küçük ölçekte zararlı.** `qwen3-0.6b` sınıfı modeller
yanıttan önce uzun bir `<think>` bloğu üretiyor. Bu blok token bütçesini
tüketiyor; `MAX_TOKENS` sınırına düşünme bloğunun *içinde* ulaşıldığında
kullanıcıya **boş yanıt** dönüyor. Yani "daha çok düşünen" model, küçük
bütçede hiç cevap veremiyor.

**Küçük modelde tekrar döngüleri.** 1.5B model belirli sorularda aynı cümleyi
tekrarlayıp bütçeyi yakıyor. Ölçüldü: bir soruda model 1024 token'ın tamamını
döngüde harcadı, yanıt 72 saniye sürdü.

İlk çözümümüz örnekleme parametresiydi (`FREQUENCY_PENALTY = 0.3`). Çalışıyordu
ama çalışma aralığı tehlikeli derecede dardı: 0.4 ve üzeri çıktının genel
kalitesini bozuyor, tam 0 göndermek modeli tamamen kilitliyordu. Yani çözüm,
tek bir modele özgü ve deneysel olarak bulunmuş kırılgan bir ayardı.

Bunu **deterministik tespitle** değiştirdik: üretilen metnin son 16 karakteri
çıktıda 3 kez tekrarlanmışsa üretim kesiliyor.

**Öğrenilen.** Örnekleme parametreleriyle yapılan düzeltmeler model değişince
geçersizleşir ve ölçüsü yoktur — "0.3 iyi, 0.4 kötü" bilgisi taşınabilir
değildir. Deterministik bir kontrol hem model-bağımsızdır hem de
**gözlemlenebilir**: döngü yakalandığında log düşüyor, sorunun sıklığı
ölçülebiliyor. Bir sorunu gizlemek ile ölçülebilir kılmak arasındaki fark budur.

Kalan sınır dürüstçe kayıtlı: kesme işlemi üretimden *sonra* çalıştığı için
çıktıyı temizliyor ama 72 saniyeyi geri getirmiyor.

---

## 8. Yerel çıkarımda darboğaz üretim değil, prompt işleme

Sezgi şunu söyler: model yavaşsa, token üretimi yavaştır. Ölçüm bunu çürüttü.

```
Vektör arama          :  0.047 ms   (21.300 sorgu/sn)
Sorgu embedding + arama:  ~1.6 sn
İlk token'a kadar      : 15.4 sn    <-- darboğaz
Üretim (19 token/sn)   :  ~1.3 sn
```

Zamanın neredeyse tamamı ilk token'dan **önce** geçiyor. Kaynağını izole etmek
için bağlam boyutunu değiştirip ölçtük:

| Bağlam | İlk token |
|---|---|
| 0 karakter | 4.08 sn |
| 500 | 6.85 sn |
| 1000 | 7.66 sn |
| 2144 (mevcut) | 16.80 sn |

Bağlam sıfırken bile 4 saniyelik sabit bir taban var; üstü prompt işleme
(prefill) maliyeti ve bağlamla birlikte hızla büyüyor.

**Öğrenilen — ve bu, sezgiye en aykırı bulgu:** Streaming'in değeri, üretim
süresinin toplam sürede baskın olmasına bağlıdır. Bizim sistemimizde üretim
16 saniyenin yalnızca 1 saniyesi. Yani **streaming, algılanan hıza neredeyse
hiçbir şey katmıyor** — kullanıcı ilk kelimeyi görmek için yine 15 saniye
bekliyor. "Streaming koyduk, hızlı hissettiriyor" cümlesi bizim ölçümümüzde
doğru değil.

Buradan çıkan mimari sonuç: yerel RAG'de bağlam uzunluğu yalnızca bir kalite
parametresi değil, **birinci dereceden bir gecikme parametresidir**. Daha çok
parça göndermek "biraz daha yavaş" değil, katlanarak daha yavaş demek.

---

## 9. Eşiğin ikinci işlevi: LLM'i hiç çağırmamak

Benzerlik eşiğini bir gürültü filtresi olarak kurmuştuk. Ölçümde ikinci bir
faydası ortaya çıktı: eşiği geçen hiçbir parça yoksa dil modeli **hiç
çalıştırılmıyor**, doğrudan "belgelerde bilgi yok" dönülüyor.

Ölçülen fark: bu yolla reddedilen bir soru 6.7 saniyede yanıtlandı; LLM'e
giden sorular ~15 saniye sürdü.

**Öğrenilen.** Aynı mekanizma hem doğruluğu (uydurma ihtimali sıfır, çünkü
model devrede değil) hem hızı (iki kattan fazla) iyileştiriyor. RAG
sistemlerinde "modeli çağırmamaya karar vermek" başlı başına bir tasarım
kararıdır ve genellikle atlanır.

---

## 10. En sinsi hata türü: yakın ama yanlış

Değerlendirmede üç bağımsız koşuda tekrarlanan tek bir cevaplanabilir hata var:

> **Soru:** Şehir içi iş yemeklerinde kişi başı üst limit nedir?
> **Belge:** "Şehir içi iş yemeklerinde kişi başı üst limit 750 TL'dir.
> Müşteri ağırlama yemeklerinde limit kişi başı 1.500 TL'dir..."
> **Yanıt:** 1.500 TL

Doğru belge getirildi, doğru parça getirildi, cevap parçanın içindeydi — model
aynı cümledeki **iki sayıdan yanlışını** seçti.

**Öğrenilen.** Bu hata retrieval ile çözülemez; parçalama stratejisiyle de
çözülemez, çünkü iki gerçek aynı cümlede. Saf bir model kavrayışı sınırıdır ve
tam da bu yüzden en tehlikeli hata türüdür: sistem kendinden emin, kaynak
gösterimi doğru, sayı belgede gerçekten geçiyor. Kullanıcının yanlış olduğunu
anlamasının hiçbir yolu yok.

Uydurma hatalarını kaynak göstererek yakalayabilirsiniz; bu hata türünü
yakalayamazsınız. Kritik alanlarda (hukuk, sağlık, finans) küçük modelle
çalışmama kararının asıl gerekçesi budur.

---

## Teknik değişiklikler ve gerekçeleri

Proje boyunca değiştirdiğimiz teknik kararlar ve **neden** değiştirdiğimiz:

**Chat modeli: `qwen3-0.6b` → `qwen2.5-1.5b` (reasoning → instruct).**
Reasoning modeli yanıttan önce `<think>` bloğu üretiyor ve bu blok token
bütçesini tüketiyor; sınıra düşünme bloğunun içinde ulaşılınca kullanıcıya
boş yanıt dönüyordu. 0.5B ise Türkçe dilbilgisinde yetersizdi. 1.5B instruct,
hedef donanıma sığan ve düşünme bloğu üretmeyen ilk seçenek.

**Embedding CPU'da, chat GPU'da.** 2 GB VRAM'e iki model aynı anda sığmıyor;
taşma sadece yavaşlatmıyor, çıktıyı da bozuyor. Hangisinin GPU'da kalacağını iş
yükünün şekli belirledi: embedding sonuçları **kalıcı** (bir parça bir kez
embed edilir, sonra veritabanında durur) ve sorgu tarafında tek kısa metin
işlenir. Chat üretimi ise her sorguda token token çalışır ve kullanıcının
beklediği gecikmenin tamamını oluşturur. Hızlandırmadan en çok fayda gören
aşama bu. Bedeli: ingestion belirgin şekilde yavaşladı — ama o tek seferlik.

**Saf dense arama → hibrit (dense + BM25).** Türkçenin sondan eklemeli yapısı
yüzünden "izin" sorgusu "izinleri" geçen parçayı kaçırıyordu. BM25 ayağı,
kullanıcının yazdığı terimin birebir geçtiği yeri buluyor.

**Skor toplama → RRF ile sıralama birleştirme.** Kosinüs 0–1 arasında,
BM25 sınırsız ve korpusa bağlı. İki skoru ağırlıklı toplamak, ölçeklerden biri
kaydığında sessizce bozulan bir sistem üretir. RRF yalnızca **sıralamaları**
kullandığı için normalizasyon gerektirmiyor.

**Embedding depolama: JSON metin → float32 BLOB.** 1024 boyutlu vektör JSON
olarak ~20 KB, float32 binary olarak 4 KB. Dörtte bir yer, ayrıştırma maliyeti
sıfır (`np.frombuffer` doğrudan okuyor).

**Python döngüsü → NumPy matris çarpımı + RAM önbelleği.** Her sorguda tüm
vektörleri diskten okuyup tek tek karşılaştırmak yerine, tüm embedding'ler tek
bir matriste tutuluyor ve benzerlik tek çarpımla hesaplanıyor. Ölçüm:
0.047 ms/sorgu. Bedeli: veri değiştiren her yolda önbelleği geçersiz kılmayı
unutmamak gerekiyor.

**Harici vektör veritabanı kullanılmadı.** Chroma/FAISS projenin temel
iddiasını bozardı: tek dosya, sunucusuz, kurulum gerektirmeyen dağıtım. Bu
ölçekte matris çarpımı zaten milisaniye mertebesinde.

**`FREQUENCY_PENALTY` → deterministik döngü tespiti.** Örnekleme ayarı
çalışıyordu ama aralığı tehlikeli derecede dardı (0.4 çıktıyı bozuyor, tam 0
modeli kilitliyor) ve tek bir modele özgüydü. Deterministik kontrol
model-bağımsız ve **gözlemlenebilir**: döngü yakalandığında log düşüyor.

**Benzerlik eşiğine ikinci bir görev.** Eşiği geçen parça yoksa dil modeli
**hiç çağrılmıyor**. Aynı mekanizma hem uydurmayı imkânsız kılıyor (model
devrede değil) hem yanıtı iki kattan fazla hızlandırıyor (6.7 sn / 15 sn).

**Prompt'ta reddetme kuralının konumu.** Ayrıntısı yukarıda: kuralı sona değil
başa koymak, reddetmeyi 1/4'ten 3/4'e çıkardı.

---

## Kendi yaptığımız metodolojik hatalar

Dürüstlük adına, ölçüm sürecinde yaptığımız iki hata:

**Kötü tasarlanmış tuzak sorusu.** "İzin günlerinde VPN parolası kaç günde bir
değişir?" sorusunu, cevabı belgelerde olmayan bir tuzak sanmıştık. Model cevap
verince "uydurdu" diye işaretledik. Kontrol edince görüldü ki parola rotasyonu
(90 gün) `bilgi_guvenligi.txt` içinde gerçekten var — model **doğru** cevap
vermişti, sadece cümleyi bozmuştu. Soruyu düzelttik, skoru düzeltmedik.
*Değerlendirme setinin kendisi de hata içerebilir ve o hatalar sistemi haksız
yere suçlar.*

**Kirli ölçüm koşulu.** İlk gecikme ölçümlerini alırken aynı makinede test
paketini de çalıştırdık; kaynak rekabeti yüzünden süreler şişti (bir yanıt 72
saniye göründü). Geç/kal sonuçları etkilenmedi ama süre verileri kullanılamaz
hale geldi ve ölçümü boş makinede tekrarlamak gerekti. *Performans ölçümü
kontrollü bir deneydir; öyle davranılmazsa üretilen sayı bir şey ifade etmez.*

---

## Bu projenin kazandırdıkları

**Bir RAG sisteminin nerede kırıldığını artık tahmin etmiyoruz, ölçüyoruz.**
Değerlendirme seti, prompt değişikliğinin etkisini (%60 → %74) rakamla
gösterebilen bir altyapı. Aynı set, model değiştirildiğinde veya eşik
oynatıldığında etkisini anında görmeyi sağlıyor. Bu, "sanırım daha iyi oldu"
ile "reddetme oranı 1/4'ten 3/4'e çıktı" arasındaki fark.

**Hangi sorunun hangi araçla çözüleceğini ayırt edebiliyoruz.** Uydurma tek bir
sorun değil; en az iki farklı mekanizması var ve biri eşikle, diğeri kesinlikle
eşikle çözülmüyor. Bu ayrımı görmeden yapılan her ayar, kör atıştır.

**Küçük model gerçekliğini biliyoruz.** Prompt sırası davranışı değiştiriyor,
reasoning modelleri küçük bütçede boş yanıt üretiyor, örnekleme ayarları
taşınabilir değil, aynı cümledeki iki sayı karışabiliyor. Bunların hiçbiri
dokümantasyonda yazmıyordu; hepsi ölçümden çıktı.

**Yerel çıkarımın maliyet yapısını biliyoruz.** Darboğaz üretim değil prefill;
bağlam uzunluğu gecikmenin birinci belirleyicisi; streaming ancak üretim
baskınsa işe yarıyor. Bu bilgi, donanım önerisinden bağlam limitine kadar her
kararı değiştiriyor.

**Ve en genel olanı:** Yapay zekâ sistemlerinde çalışan kodla doğru davranan
sistem aynı şey değil. Aradaki boşluk yalnızca ölçümle görülür ve ölçülmeyen
sistem, en güvendiğiniz anda uydurur.
