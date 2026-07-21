# ADR-0005: Kimlik dogrulama ve rol tabanli erisim

**Durum:** Kabul edildi
**Tarih:** 2026-07-21

## Baglam

Program plani kimlik dogrulama **istemiyordu**. Planin hedefi tek kullanicili,
tek makinede calisan bir ogrenci projesiydi.

Ancak bu uygulamanin gercek kullanim senaryosu, kurumsal ic belgeler (izin
politikasi, masraf politikasi, BT prosedurleri) uzerinde soru-cevap. Bu tur bir
sistem bir ekip tarafindan kullanildigi anda su sorular dogar: belge yukleyip
silmeye kim yetkili, bilgi tabanini kim sifirlayabilir, kim ne sordu.

Bu ADR, plandan bilincli bir sapmayi kayit altina alir.

## Karar

Rol tabanli kimlik dogrulama eklenir: `admin` ve `user`.

- **Okuma yollari** (`/query`, `/documents`, `/auth/me`) giris yapmis herhangi
  bir kullaniciya acik.
- **Degistirme yollari** (`/ingest/*`, `/documents/{id}` silme, `/stats`,
  `/reset`, kullanici yonetimi) yalnizca `admin`.

Destekleyici kararlar:

| Karar | Gerekce |
|---|---|
| Parola hash'i **scrypt** (`hashlib`, standart kutuphane) | KDF kasitli olarak yavas **ve** bellek-yogun; GPU ile paralel kirma saldirisini pahalilastirir. Yeni bagimlilik gerektirmez. |
| Her hash'te rastgele salt, parametreler hash string'ine gomulu | Ayni parolaya sahip iki kullanici farkli hash uretir. Gomulu parametreler ileride maliyeti artirmayi mumkun kilar (`needs_rehash`). |
| Dogrulamada `hmac.compare_digest` | Sabit zamanli karsilastirma; normal `==` erken cikis yaptigi icin zamanlama sizintisi verir. |
| Oturum token'i sunucu tarafinda saklanir (JWT degil) | Cikis (logout) aninda gercekten gecerliligini yitirir. JWT'de iptal ayri bir kara liste altyapisi gerektirir. |
| Ilk admin parolasi `secrets.token_urlsafe(12)` ile **rastgele** uretilir | Sabit varsayilan parola (`admin/admin`) ile teslim edilen sistemler pratikte hic degistirilmiyor. |
| `auth.db`, `knowledge_base.db`'den **ayri dosya** | `/reset` bilgi tabanini siler; hesaplari ve denetim kaydini silmemeli. |
| Denetim kaydi (audit log) | Kurumsal ortamda "kim neyi ne zaman degistirdi" sorusu cevaplanabilir olmali. |
| 5 basarisiz denemede **5 dakikalik** kilit | scrypt tek basina yeterli fren degil (~15 deneme/sn ag uzerinden). Kilit KISA tutuldu: kalici kilit, saldirganin bir calisani surekli yanlis parola girerek sistem disi birakmasina izin verirdi. |

## Sonuclar

- Proje plandaki kapsamin uzerine cikti. Bu, sunumda gerekcelendirilmesi
  gereken bir sapmadir - bu ADR o gerekcedir.
- Kimlik dogrulama, tasima guvenligini **saglamaz**. Duz HTTP uzerinde parola ve
  oturum token'i acik metin gider. Bkz. [ADR-0006](0006-ag-erisimi-ve-tasima-guvenligi.md).
- Test yuzeyi buyudu: `tests/test_auth.py`, `tests/test_api_auth.py`,
  `tests/test_password.py`.
