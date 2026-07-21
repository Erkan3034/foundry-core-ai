"""
Foundry RAG Assistant - Metin Normalizasyonu ve FTS Sorgu Uretimi

Turkce'ye ozgu iki problemi cozer:

1. DIAKRITIK UYUSMAZLIGI
   Korpustaki belgeler Turkce karaktersiz yazilmis olabilir ("GUVENLIGI"),
   kullanici ise diakritikle yazar ("güvenliği"). Anahtar kelime aramasinin
   calismasi icin iki taraf da ayni sekilde katlanmalidir.

2. SONDAN EKLEMELI YAPI
   "parola" sorgusu "parolalari" gecen parcayi bulmalidir. Turkce'de ekler
   sona geldigi icin ON-EK (prefix) eslesmesi ucuz ve etkili bir stemmer
   yerine gecer: "parol*" -> parola, parolalar, parolamiz.
"""

import re

# Turkce harflerin ASCII karsiliklari.
# NOT: unicode61 remove_diacritics'e guvenilmiyor; 'i' (U+0131) bir
# diakritik degil ayri bir harftir ve otomatik katlanmaz.
_TR_MAP = str.maketrans({
    "ç": "c", "Ç": "c",
    "ğ": "g", "Ğ": "g",
    "ı": "i", "I": "i",
    "İ": "i", "i": "i",
    "ö": "o", "Ö": "o",
    "ş": "s", "Ş": "s",
    "ü": "u", "Ü": "u",
    "â": "a", "Â": "a",
    "î": "i", "Î": "i",
    "û": "u", "Û": "u",
})

# Prefix eslesmesi icin terimin kirpilacagi uzunluk.
# 5 karakter: "parolami" -> "parol*" (parolalar'i yakalar),
# "izin" (4) oldugu gibi kalir. Daha kisa tutmak yanlis eslesmeyi artirir.
STEM_PREFIX_LEN = 5

# FTS5 sozdizimini bozabilecek / operator anlami tasiyan karakterler.
_FTS_UNSAFE = re.compile(r'[^\w\s]', re.UNICODE)

# FTS5 operatorleri terim olarak gelirse tirnaklanmali yerine atilir.
_FTS_KEYWORDS = {"and", "or", "not", "near"}


def normalize_tr(text: str) -> str:
    """Turkce metni kucuk harfe cevirip diakritikleri ASCII'ye katla.

    'GÜVENLİĞİ' -> 'guvenligi',  'Yıllık İzin' -> 'yillik izin'
    """
    if not text:
        return ""
    # Once diakritikleri katla, SONRA kucult: Python'un lower()'i
    # 'I' -> 'i' yapar ama Turkce'de 'I' -> 'ı'dir; katlama sonrasi
    # ikisi de 'i' oldugu icin sira onemli.
    return text.translate(_TR_MAP).lower()


def build_fts_query(query: str) -> str:
    """Kullanici sorgusundan guvenli bir FTS5 MATCH ifadesi uret.

    Terimler normalize edilir, kok prefix'ine kirpilir ve OR ile baglanir.
    Kullanici girdisindeki FTS5 operatorleri temizlenir (injection korumasi).

    'Yıllık İZİN' -> 'yilli* OR izin*'
    """
    normalized = normalize_tr(query)
    # Operator karakterlerini bosluga cevir; geriye harf/rakam/alt cizgi kalir
    cleaned = _FTS_UNSAFE.sub(" ", normalized)

    terms = []
    for term in cleaned.split():
        if len(term) < 2 or term in _FTS_KEYWORDS:
            continue
        stem = term[:STEM_PREFIX_LEN]
        terms.append(f"{stem}*")

    return " OR ".join(terms)
