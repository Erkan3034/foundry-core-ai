# 2 Dakikalık Video — Konuşma Metni

**Slayt:** `docs/sunum-slayt.html` — üzerinde okunacak metin yok, sadece
mimari diyagramı ve iki ölçüm grafiği var. Anlatılacak her şey bu dosyada.

**Kurgu:** Slayt açık başlıyor. Ortada bir kez sohbet arayüzüne geçilip tek
soru soruluyor; yanıt ~15 saniyede geliyor ve o süre boş bırakılmıyor.

**Hedef: 1:56** · ~280 kelime (≈145 kelime/dk)

Problemi tanıtmıyoruz, konsept zaten belli. Eksen: **ne yaptım → nasıl
yaptım → teknik olarak ne öğrendim → ne kattı.**

---

## Zaman planı

| Süre | Ekran | İçerik |
|---|---|---|
| 0:00–0:12 | Slayt · üst şerit | Ne yaptım |
| 0:12–0:16 | Sohbet | Enter'a bas |
| 0:16–0:40 | Sohbet (üretiliyor) | Nasıl yaptım — indeksleme hattı |
| 0:40–0:50 | Sohbet (yanıt geldi) | Yanıt + kaynak + eşik davranışı |
| 0:50–1:48 | Slayt · 2. şerit ve grafikler | Teknik olarak ne öğrendim |
| 1:48–1:56 | Slayt | Ne kattı + kapanış |

---

## Metin

> **[0:00 · SLAYT]**
> Microsoft Foundry Local üzerinde çalışan, tamamen cihaz içi bir Türkçe
> RAG asistanı yaptım. Ekranda gördüğünüz hattın tamamı — embedding
> modeli, vektör deposu, arama ve dil modeli — tek makinede çalışıyor,
> dışarıya hiçbir ağ çağrısı yok.

> **[0:12 · SOHBETE GEÇ — Enter'a bas]**
> Bir soru sorayım, yanıt gelene kadar nasıl kurduğumu anlatayım.

> **[0:16 · YANIT ÜRETİLİRKEN — durma, anlat]**
> Belgeler örtüşmeli parçalara bölünüp embedding'e veriliyor. Vektörleri
> JSON metni yerine float32 BLOB olarak saklıyorum: 1024 boyutlu bir
> vektör 20 kilobayt yerine 4 kilobayt yer kaplıyor ve `np.frombuffer`
> sıfır ayrıştırma maliyetiyle okuyor.
> Aramada her sorguda diski okuyup tek tek karşılaştırmak yerine bütün
> embedding'leri bellekte tek bir matriste tutuyorum; benzerlik tek matris
> çarpımı, sorgu başına 0.047 milisaniye. Bu yüzden Chroma ya da FAISS
> gibi harici bir vektör veritabanına hiç ihtiyaç duymadım — sistem tek
> SQLite dosyası olarak kalabildi.

> **[0:40 · YANIT GELDİ — kaynağı göster]**
> Yanıt geldi, altında hangi dosyadan geldiği yazıyor. Bir de şu var:
> benzerlik eşiğini geçen hiçbir parça yoksa dil modeli hiç çağrılmıyor,
> sistem doğrudan "belgelerde bilgi yok" diyor. Uydurma ihtimali sıfır,
> üstelik iki kat hızlı.

> **[0:50 · SLAYDA DÖN — sorgu şeridini göster]**
>
> **Birincisi: saf dense retrieval Türkçede yetmiyor.** Dil sondan
> eklemeli olduğu için yüzey formları ayrışıyor; "izin" sorgusu
> "izinleri" geçen parçayı kaçırıyordu. BM25 ekleyip Reciprocal Rank
> Fusion ile birleştirdim. RRF'i seçmemin sebebi önemli: kosinüs sıfır
> ile bir arasında, BM25 ise sınırsız ve korpusa bağlı. Skorları
> toplasaydım ölçeklerden biri kaydığında sistem sessizce bozulurdu; RRF
> yalnızca sıralamaları kullanıyor.
>
> **İkincisi: CPU–GPU ayrımına iş yükünün şekline bakarak karar verdim.**
> İki model 2 gigabayt VRAM'e sığmıyor, ve taşma sadece yavaşlatmıyor,
> çıktıyı da bozuyor. Embedding'i CPU'ya aldım çünkü sonucu kalıcı — bir
> kez hesaplanıp veritabanında duruyor. Chat üretimi ise her soruda
> baştan çalışıyor ve kullanıcının beklediği gecikmenin tamamını o
> oluşturuyor; GPU'yu ona ayırdım.

> **[≈1:25 · ALTTAKİ İKİ GRAFİĞİ GÖSTER]**
>
> **Üçüncüsü, ve en şaşırtıcısı: darboğaz üretim değil, prefill.**
> Sağdaki grafikte görüyorsunuz — 16 saniyelik yanıtın sadece 1.3 saniyesi
> üretim, 13.8 saniyesi prompt işleme. Soldaki grafikte de bağlam boyutunu
> değiştirip ölçtüğüm hali var: sıfır karakterde 4 saniye, iki bin
> karakterde 17. Yani bağlam uzunluğu bir kalite ayarı değil, birinci
> dereceden bir gecikme parametresi. Ve üretim baskın olmadığı için
> streaming algılanan hıza neredeyse hiçbir şey katmıyor — bunu ölçmeden
> önce tam tersini varsayıyordum.

> **[1:48 · KAPANIŞ]**
> Bu projenin bana kattığı şey şu: bir RAG sisteminin nerede kırıldığını
> artık tahmin etmiyorum, ölçüyorum. Kod, sekiz mimari karar kaydı ve
> ölçümlerin tamamı GitHub'da.

---

## Sorulacak soru

Kayıttan **önce** soru kutusuna yazılı olsun; kayıtta yalnızca Enter'a bas.

```
Yıllık izin kaç gün?
```

Değerlendirmede tutarlı biçimde doğru cevaplanan sınıfta
(`eval/RESULTS.md`); yanıtın altında kaynak dosya görünür.

---

## Kayıttan önce kontrol listesi

- [ ] `python api_server.py` çalışıyor, `/health` yanıt veriyor
- [ ] **Modeller önceden yüklendi** — kayıttan önce bir ısınma sorusu sor,
      yoksa ilk soru model yükleme yüzünden dakikalarca sürer
- [ ] Aynı soruyu kayıttan önce bir kez dene, beklenen yanıtı verdiğini gör
- [ ] Slayt tam ekran (F11), tarayıcı zoom %100
- [ ] Sohbet ayrı pencerede hazır, soru kutusuna yazılmış
- [ ] Bildirimler kapalı, gereksiz sekmeler kapalı
- [ ] Mikrofon testi: 10 saniye kaydet, dinle

## Ritim notları

**Enter'a basar basmaz duraklamadan anlatıma geç.** Yanıt ~15. saniyede
ekranda belirecek; cümleni bitir, sonra yanıta dön. O 15 saniye videonun
sekizde biri.

**Süreyi aşarsan kesilecek ilk yerler:** 0:16 bloğundaki "sistem tek SQLite
dosyası olarak kalabildi" ve kapanıştaki "sekiz mimari karar kaydı".

**Değiştirme seçeneği:** Üçüncü maddeyi retrieval tarafına çevirmek
istersen — "benzerlik skoru cevaplanabilirliğin göstergesi değil;
uydurulan bir soru 0.482 benzerlikle parça getirdi, doğru cevapların
çoğundan yüksek. Çünkü 'ilgili mi' ile 'cevabı içeriyor mu' ayrı sorular,
kosinüs yalnızca birincisini ölçüyor." Ama o zaman alttaki iki grafiği
göstermemiş olursun.
