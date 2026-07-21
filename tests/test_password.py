"""
Foundry RAG Assistant - Parola Hash Testleri

Parolalar ASLA duz metin veya duz SHA-256 ile saklanmaz. scrypt bir anahtar
turetme fonksiyonudur (KDF): kasitli olarak yavas ve bellek-yogundur, boylece
veritabani calinsa bile kaba kuvvet saldirisi pratik olmaz.

hashlib.scrypt Python standart kutuphanesindedir - yeni bagimlilik yok.
"""

import pytest

from password import hash_password, verify_password, needs_rehash


class TestHashing:

    def test_same_password_gives_different_hashes(self):
        """Rastgele salt: ayni parola iki farkli hash uretmeli.

        Aksi halde saldirgan ayni hash'e sahip kullanicilari eslestirebilir
        ve rainbow table saldirisi mumkun olur.
        """
        a = hash_password("AyniParola123")
        b = hash_password("AyniParola123")
        assert a != b

    def test_hash_is_not_plaintext(self):
        h = hash_password("gizliParola")
        assert "gizliParola" not in h

    def test_hash_is_versioned(self):
        """Format ileride KDF degistirebilmek icin surumlenmis olmali."""
        h = hash_password("parola")
        assert h.startswith("scrypt$")
        # scrypt$n$r$p$salt$hash
        assert len(h.split("$")) == 6

    def test_rejects_empty_password(self):
        with pytest.raises(ValueError):
            hash_password("")

    def test_handles_unicode_password(self):
        """Turkce karakterli parola calismali."""
        h = hash_password("Şifrem_Çok_Güçlü_ğüı")
        assert verify_password("Şifrem_Çok_Güçlü_ğüı", h)

    def test_handles_long_password(self):
        uzun = "x" * 500
        assert verify_password(uzun, hash_password(uzun))


class TestVerification:

    def test_accepts_correct_password(self):
        h = hash_password("DogruParola")
        assert verify_password("DogruParola", h) is True

    def test_rejects_wrong_password(self):
        h = hash_password("DogruParola")
        assert verify_password("YanlisParola", h) is False

    def test_rejects_case_change(self):
        h = hash_password("Parola")
        assert verify_password("parola", h) is False

    def test_rejects_empty_input(self):
        h = hash_password("Parola")
        assert verify_password("", h) is False

    def test_rejects_malformed_hash_without_crashing(self):
        """Bozuk/eski kayit istisna firlatip girisi cokertmemeli."""
        for bozuk in ["", "garbage", "scrypt$abc", "scrypt$1$2$3$4", "$$$$$"]:
            assert verify_password("parola", bozuk) is False

    def test_rejects_none_hash(self):
        assert verify_password("parola", None) is False


class TestRehashPolicy:
    """Parametreler guclendiginde eski hash'ler tespit edilebilmeli."""

    def test_current_hash_does_not_need_rehash(self):
        assert needs_rehash(hash_password("parola")) is False

    def test_weaker_parameters_need_rehash(self):
        zayif = "scrypt$1024$8$1$" + "a" * 32 + "$" + "b" * 64
        assert needs_rehash(zayif) is True

    def test_malformed_hash_needs_rehash(self):
        assert needs_rehash("garbage") is True
