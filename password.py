"""
Foundry RAG Assistant - Parola Hash'leme

scrypt kullanilir (hashlib, standart kutuphane - yeni bagimlilik yok).

NEDEN duz SHA-256 DEGIL:
SHA-256 hizli olmak icin tasarlanmistir; modern bir GPU saniyede milyarlarca
SHA-256 hesaplar. Veritabani sizarsa parolalar saatler icinde kirilir.
scrypt bir KDF'dir: kasitli olarak yavas (~60ms) VE bellek-yogundur, bu da
GPU/ASIC ile paralellestirmeyi pahali hale getirir.

Hash formati (surumlenmis, ileride KDF degistirilebilsin diye):
    scrypt$n$r$p$<salt_hex>$<hash_hex>
"""

import hashlib
import hmac
import secrets

# scrypt parametreleri.
# n=2**14 (16384) bu makinede ~60ms/hash veriyor: kaba kuvvete karsi yeterince
# yavas, girise engel olmayacak kadar hizli. Donanim guclendikce artirilmali;
# needs_rehash() eski kayitlari tespit eder.
SCRYPT_N = 2 ** 14
SCRYPT_R = 8
SCRYPT_P = 1
SALT_BYTES = 16
KEY_LEN = 32

_ALGORITHM = "scrypt"


def hash_password(password: str) -> str:
    """Parolayi rastgele salt ile hash'le.

    Ayni parola her cagrida FARKLI hash uretir (rastgele salt); bu, iki
    kullanicinin ayni parolayi kullandiginin anlasilmasini ve rainbow table
    saldirilarini engeller.
    """
    if not password:
        raise ValueError("Parola bos olamaz")

    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=KEY_LEN,
    )
    return f"{_ALGORITHM}${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def _parse(stored: str):
    """Saklanan hash'i bilesenlerine ayir. Bozuksa None dondurur."""
    if not stored or not isinstance(stored, str):
        return None
    parts = stored.split("$")
    if len(parts) != 6 or parts[0] != _ALGORITHM:
        return None
    try:
        n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
        salt = bytes.fromhex(parts[4])
        digest = bytes.fromhex(parts[5])
    except (ValueError, TypeError):
        return None
    if not salt or not digest:
        return None
    return n, r, p, salt, digest


def verify_password(password: str, stored: str) -> bool:
    """Parolayi saklanan hash'e karsi dogrula.

    Bozuk/eksik kayitlarda istisna FIRLATMAZ, False doner: tek bozuk satir
    tum giris akisini cokertmemeli.
    """
    if not password:
        return False

    parsed = _parse(stored)
    if parsed is None:
        return False

    n, r, p, salt, expected = parsed
    try:
        candidate = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt, n=n, r=r, p=p, dklen=len(expected),
        )
    except (ValueError, MemoryError):
        # Gecersiz parametreler (or. n iki'nin kuvveti degil)
        return False

    # compare_digest: sabit zamanli karsilastirma. Normal '==' erken cikis
    # yaptigi icin zamanlama saldirisina acik olurdu.
    return hmac.compare_digest(candidate, expected)


def needs_rehash(stored: str) -> bool:
    """Hash mevcut parametrelerin altindaysa True.

    Donanim guclendikce SCRYPT_N artirilir; kullanici bir sonraki basarili
    girisinde parolasi sessizce yeniden hash'lenebilir.
    """
    parsed = _parse(stored)
    if parsed is None:
        return True
    n, r, p, _, _ = parsed
    return n < SCRYPT_N or r < SCRYPT_R or p < SCRYPT_P
