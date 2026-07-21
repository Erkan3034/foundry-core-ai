# Sunum Notlari - 2 Dakikalik Video

Program planinin sundugu dort baslik: **problem**, **bilesenler**,
**canli demo (bilmedigini soyledigi bir ornek dahil)**, **cikarimlar**.

## Zaman plani

| Sure | Bolum | Ekranda ne var |
|---|---|---|
| 0:00-0:15 | Problem | Web arayuzu acik, bos sohbet ekrani |
| 0:15-0:40 | Ne yaptim | Mimari semasi (README'deki blok diyagram) |
| 0:40-1:10 | Demo 1 - cevap + kaynak | Canli sorgu |
| 1:10-1:25 | Demo 2 - bilmedigini soylemesi | Canli sorgu |
| 1:25-1:50 | Ne ogrendim | `eval/RESULTS.md` ekranda |
| 1:50-2:00 | Kapanis | GitHub deposu |

## Konusma metni

> **[0:00 - Problem]**
> Sirketlerin ic belgeleri var: izin politikasi, masraf kurallari, BT
> prosedurleri. Calisanlar bunlari surekli soruyor. Ama bu belgeleri bulut
> tabanli bir yapay zekaya veremezsiniz. Ben de tamamen cihaz uzerinde calisan,
> internete hic cikmayan bir soru-cevap asistani yaptim.

> **[0:15 - Ne yaptim]**
> Microsoft Foundry Local ile dil modeli ve embedding modeli bilgisayarda
> calisiyor. Belgeler parcalara bolunup vektore cevriliyor ve SQLite'ta
> saklaniyor. Soru gelince once ilgili parcalar bulunuyor, sonra bunlar
> modele baglam olarak veriliyor. Buna RAG deniyor.
> Aramayi iki ayakli yaptim: anlamsal arama ve anahtar kelime aramasi.
> Cunku Turkce sondan eklemeli; "izin" ile "izinleri" tek basina anlamsal
> aramada her zaman eslesmiyordu.

> **[0:40 - Demo 1]**
> *(Sor: "Yillik izin kac gun?")*
> Yanit geliyor ve altinda kaynak dosyayi gosteriyor. Kullanici cevabi
> dogrulayabiliyor. Yanit token token akiyor, tamamlanmasini beklemiyoruz.

> **[1:10 - Demo 2]**
> *(Sor: "Sirketin cirosu ne kadar?")*
> Bu bilgi belgelerde yok. Sistem uydurmuyor, bilmedigini soyluyor.
> Burada bir detay var: benzerlik esigini gecen hicbir parca bulunamazsa
> dil modeli **hic calistirilmiyor**. Yani bu yanit hem daha hizli geliyor
> hem de uydurma ihtimali sifir.

> **[1:25 - Ne ogrendim]**
> Projenin bana en cok sey ogreten kismi buydu.
> 155 birim testim vardi ve hepsi geciyordu. Ama bu testler kodun
> calistigini gosteriyordu, asistanin **dogru cevap verdigini** degil.
> Bunu olcmek icin ayri bir degerlendirme seti yazdim: cevabi belgelerde
> olan sorular, olmayan sorular, ve bir de tuzak sorular.
> Sonuc suydu: belgede olan sorularin neredeyse hepsini dogru cevapliyordu,
> ama belgede **olmayan** sorularda uyduruyordu. Bir seferinde toplanti
> salonunun kirasi diye belgelerde hic gecmeyen bir rakam uretti.
> Sebebini buldum: sistem promptunda "bilmiyorsan bilmiyorum de" kurali
> en sonda yaziyordu ve kucuk model onu yok sayiyordu. Kurali en basa,
> ilk kontrol olarak tasidim.
> Buradan cikardigim sey: bir RAG sisteminde testlerin gecmesi yeterli
> degil, yanit kalitesini ayrica ve duzenli olcmek gerekiyor.

> **[1:50 - Kapanis]**
> Kod, mimari karar kayitlari ve degerlendirme sonuclari GitHub'da.

## Demo oncesi kontrol listesi

- [ ] `python api_server.py` calisiyor, `/health` yanit veriyor
- [ ] Modeller **onceden yuklenmis** (ilk sorgu model yuklemesi yuzunden yavas;
      kayittan once bir isinma sorusu sor)
- [ ] Demo 1 ve Demo 2 sorularini kayittan once bir kez dene, gercekten
      beklenen davranisi verdigini gor
- [ ] Tarayici zoom seviyesi okunakli, gereksiz sekmeler kapali
- [ ] `eval/RESULTS.md` ayri bir sekmede acik

> **Not:** Videodaki "ne ogrendim" bolumunun uzun hali
> [ogrenilenler.md](ogrenilenler.md) icinde. Sunumda sorulursa oradaki
> bulgulara referans verebilirsin; ozellikle "benzerlik skoru
> cevaplanabilirligin gostergesi degil" ve "darbogaz uretim degil prefill"
> baslıklari, yuzeysel bir RAG anlatimindan ayrisan kisimlar.

## Sorulursa hazir cevaplar

**"Plan CLI yeterli diyordu, neden bu kadar buyuttun?"**
Hedef senaryo tek kullanicili degil, kurumsal ic belgeler. Bir ekip
kullandigi anda "belge yuklemeye kim yetkili" sorusu doguyor. Karari ve
takasini [ADR-0005](adr/0005-kimlik-dogrulama.md)'te yazdim.

**"Neden plandaki Phi-3.5 Mini degil?"**
Hedef makinede 2 GB VRAM var; 3-5B model sigmiyor. Ayrica denedigim reasoning
modelleri yanittan once `<think>` blogu uretip token butcesini tuketiyordu.
[ADR-0001](adr/0001-chat-modeli-secimi.md).

**"Yanit sureleri plandaki 1-3 saniyeden yavas."**
Dogru. Olculen medyan yanit suresi `eval/RESULTS.md` icinde. Sebebi donanim:
embedding modelini CPU'ya almak zorunda kaldim cunku iki model 2 GB VRAM'e
sigmiyor ([ADR-0003](adr/0003-model-cihaz-dagilimi.md)). Streaming sayesinde
kullanicinin **ilk token'i gorme** suresi toplam sureden belirgin sekilde kisa.

**"Hala uyduruyor mu?"**
Kalan durumlar `eval/RESULTS.md` icinde acikca listeli. Bunu gizlemek yerine
olculebilir hale getirdim; bir sonraki adim benzerlik esigini ayri bir
dogrulama setiyle kalibre etmek.
