"""
Foundry RAG Assistant - Kimlik Dogrulama

Kullanici hesaplari ve oturumlar, bilgi tabanindan AYRI bir SQLite dosyasinda
(auth.db) tutulur. Gerekcesi:
  - POST /reset bilgi tabanini siler; hesaplar silinmemeli
  - Bilgi tabani yedegi parola hash'i tasimamali
  - Iki dosyaya farkli dosya izni verilebilir

Oturumlar JWT DEGIL, sunucuda saklanan rastgele token'lardir. JWT iptal
edilemez: bir calisan isten ayrildiginda token'i suresi dolana kadar gecerli
kalirdi. Sunucu tarafi oturum aninda silinebilir.

LDAP/Active Directory entegrasyonu icin: authenticate() disaridan
degistirilebilir tek giris noktasidir; kurumsal dizin kullanacak firma
yalnizca onu degistirir, geri kalan kod ayni kalir.
"""

import logging
import secrets
import sqlite3
import hashlib
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from password import hash_password, verify_password

logger = logging.getLogger(__name__)

ROLES = ("admin", "user")
MIN_PASSWORD_LENGTH = 8
DEFAULT_SESSION_TTL_SECONDS = 12 * 3600  # bir is gunu

# Kaba kuvvet korumasi.
#
# scrypt tek basina bir fren (~60 ms/deneme) ama yeterli degil: ag uzerinden
# saniyede ~15 deneme, gun boyunca milyonu asar. N basarisiz denemeden sonra
# hesap KISA SURELIGINE kilitlenir.
#
# Kilit suresi bilerek kisa tutuldu: kalici kilit, saldirganin bir calisani
# surekli yanlis parola girerek sistem disi birakmasina (hizmet engelleme)
# izin verirdi. 5 dakika, kaba kuvveti pratikte imkansiz kilarken mesru
# kullaniciyi yalnizca bir kahve molasi kadar bekletir.
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 300

# Kullanici bulunamadiginda da dogrulama maliyeti odenir ki saldirgan
# yanit suresinden kullanici adinin var olup olmadigini anlayamasin.
_DUMMY_HASH = hash_password("dummy-password-for-timing-equalization")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    """Oturum token'i veritabaninda HASH'LI saklanir.

    Parola gibi yavas KDF gerekmez: token zaten 256 bit rastgeledir, kaba
    kuvvetle tahmin edilemez. Amac, DB sizarsa token'larin dogrudan
    kullanilamamasi.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthStore:
    """auth.db uzerindeki SQLite islemleri."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
            yield conn
        finally:
            conn.close()

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    must_change_password INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_login_at TEXT,
                    failed_attempts INTEGER NOT NULL DEFAULT 0,
                    locked_until TEXT
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT NOT NULL,
                    detail TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
            """)
            self._migrate(conn)
            conn.commit()

    @staticmethod
    def _migrate(conn):
        """Var olan auth.db dosyalarini guncel semaya tasi.

        Yeni kurulumda CREATE TABLE kolonlari zaten iceriyor; bu adim
        yalnizca onceki surumden gelen dosyalar icindir. Musteri makinesinde
        veri kaybi olmadan guncelleme yapilabilmesi icin gereklidir.
        """
        existing = {r["name"] for r in conn.execute("PRAGMA table_info(users)")}

        for column, ddl in (
            ("failed_attempts", "INTEGER NOT NULL DEFAULT 0"),
            ("locked_until", "TEXT"),
        ):
            if column not in existing:
                conn.execute(f"ALTER TABLE users ADD COLUMN {column} {ddl}")
                logger.info(f"auth.db semasi guncellendi: users.{column} eklendi")

        # Kullanici adlari YAZILIRKEN kucuk harfe cevriliyor, ARANIRKEN de
        # oyle; ama SQLite karsilastirmasi harf duyarli. Normalize edilmemis
        # bir satir olusursa (elle duzenleme, eski surum, LDAP aktarimi) o
        # hesap ARTIK BULUNAMAZ: giris de, parola sifirlama da basarisiz olur
        # ve kullanici kendi sisteminden kilitlenir. Sahada yasandi.
        for row in conn.execute("SELECT id, username FROM users").fetchall():
            normalized = (row["username"] or "").strip().lower()
            if normalized == row["username"]:
                continue

            clash = conn.execute(
                "SELECT id FROM users WHERE username = ? AND id != ?",
                (normalized, row["id"])
            ).fetchone()
            if clash:
                # Iki satir ayni hesaba cozulur; birlestirme kullanicinin
                # karari oldugu icin dokunulmaz, yalnizca uyarilir.
                logger.warning(
                    f"'{row['username']}' -> '{normalized}' donusturulemedi: "
                    f"'{normalized}' zaten var (id={clash['id']}). "
                    f"Hesaplardan birini elle silin veya yeniden adlandirin."
                )
                continue

            conn.execute("UPDATE users SET username = ? WHERE id = ?",
                         (normalized, row["id"]))
            logger.warning(
                f"Kullanici adi normallestirildi: '{row['username']}' -> '{normalized}' "
                f"(bu hesap aksi halde giris yapamazdi)"
            )


class AuthService:
    """Hesap, oturum ve denetim kaydi islemleri."""

    def __init__(self, store: AuthStore):
        self.store = store

    # ---------------------------------------------------------------- kullanici

    @staticmethod
    def _normalize_username(username: str) -> str:
        """'Ayse' ve 'ayse' ayni hesaptir; kafa karisikligini onler."""
        return (username or "").strip().lower()

    @staticmethod
    def _validate_password(password: str):
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Parola en az {MIN_PASSWORD_LENGTH} karakter olmali")

    def create_user(self, username: str, password: str, role: str = "user") -> dict:
        username = self._normalize_username(username)
        if not username:
            raise ValueError("Kullanici adi bos olamaz")
        if role not in ROLES:
            raise ValueError(f"Gecersiz rol: {role}. Gecerli: {ROLES}")
        self._validate_password(password)

        with self.store._connect() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing:
                raise ValueError(f"'{username}' zaten kayitli")

            cursor = conn.execute(
                """INSERT INTO users
                   (username, password_hash, role, is_active, must_change_password, created_at)
                   VALUES (?, ?, ?, 1, 1, ?)""",
                (username, hash_password(password), role, _now().isoformat())
            )
            conn.commit()
            user_id = cursor.lastrowid

        logger.info(f"Kullanici olusturuldu: {username} ({role})")
        return self.get_user(user_id)

    def get_user(self, user_id: int) -> Optional[dict]:
        with self.store._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._to_user_dict(row)

    def get_user_by_username(self, username: str) -> Optional[dict]:
        with self.store._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (self._normalize_username(username),)
            ).fetchone()
        return self._to_user_dict(row)

    def list_users(self) -> List[dict]:
        with self.store._connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY username").fetchall()
        return [self._to_user_dict(r) for r in rows]

    @staticmethod
    def _to_user_dict(row) -> Optional[dict]:
        if row is None:
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
            "is_active": bool(row["is_active"]),
            "must_change_password": bool(row["must_change_password"]),
            "created_at": row["created_at"],
            "last_login_at": row["last_login_at"],
        }

    def deactivate_user(self, user_id: int):
        """Hesabi kapat ve TUM aktif oturumlarini dusur."""
        with self.store._connect() as conn:
            conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()
        self.log_action(user_id, "user_deactivated", None)

    def activate_user(self, user_id: int):
        with self.store._connect() as conn:
            conn.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
            conn.commit()

    # ------------------------------------------------------------ dogrulama

    def authenticate(self, username: str, password: str,
                     ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS) -> Optional[str]:
        """Kimlik dogrula ve oturum token'i dondur. Basarisizsa None.

        LDAP/AD entegrasyonu icin degistirilecek tek nokta burasidir.
        """
        username = self._normalize_username(username)

        with self.store._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if row is None:
            # Kullanici yok: yine de hash maliyetini ode ki yanit suresi
            # var olan kullaniciyla ayni olsun (kullanici adi sizdirmaz).
            verify_password(password or "x", _DUMMY_HASH)
            self._log(None, username, "login_failed", "kullanici bulunamadi")
            return None

        if not row["is_active"]:
            self._log(row["id"], username, "login_failed", "hesap kapali")
            return None

        # Kilit kontrolu parola dogrulamasindan ONCE: kilitliyken dogru parola
        # da kabul edilmez, aksi halde kilit bir sey ifade etmezdi.
        locked_until = row["locked_until"]
        if locked_until and datetime.fromisoformat(locked_until) > _now():
            # Yanit suresi normal basarisiz girisle ayni kalsin diye hash
            # maliyeti yine odenir; kilidin varligi zamanlamadan anlasilmasin.
            verify_password(password or "x", _DUMMY_HASH)
            self._log(row["id"], username, "login_failed", "hesap gecici kilitli")
            return None

        if not verify_password(password, row["password_hash"]):
            self._register_failed_attempt(row, username)
            return None

        token = secrets.token_urlsafe(32)
        expires = _now() + timedelta(seconds=ttl_seconds)

        with self.store._connect() as conn:
            conn.execute(
                "INSERT INTO sessions (token_hash, user_id, created_at, expires_at) "
                "VALUES (?, ?, ?, ?)",
                (_hash_token(token), row["id"], _now().isoformat(), expires.isoformat())
            )
            # Basarili giris sayaci sifirlar ve varsa kilidi kaldirir.
            conn.execute(
                "UPDATE users SET last_login_at = ?, failed_attempts = 0, "
                "locked_until = NULL WHERE id = ?",
                (_now().isoformat(), row["id"])
            )
            conn.commit()

        self._log(row["id"], username, "login", None)
        return token

    def _register_failed_attempt(self, row, username: str):
        """Basarisiz denemeyi say; esige ulasilinca hesabi gecici kilitle."""
        attempts = (row["failed_attempts"] or 0) + 1

        if attempts >= MAX_FAILED_ATTEMPTS:
            locked_until = _now() + timedelta(seconds=LOCKOUT_SECONDS)
            with self.store._connect() as conn:
                conn.execute(
                    "UPDATE users SET failed_attempts = 0, locked_until = ? WHERE id = ?",
                    (locked_until.isoformat(), row["id"])
                )
                conn.commit()
            logger.warning(
                f"'{username}' hesabi {MAX_FAILED_ATTEMPTS} basarisiz denemeden sonra "
                f"{LOCKOUT_SECONDS // 60} dakika kilitlendi"
            )
            self._log(row["id"], username, "account_locked",
                      f"{MAX_FAILED_ATTEMPTS} basarisiz deneme")
            return

        with self.store._connect() as conn:
            conn.execute(
                "UPDATE users SET failed_attempts = ? WHERE id = ?",
                (attempts, row["id"])
            )
            conn.commit()
        self._log(row["id"], username, "login_failed",
                  f"hatali parola ({attempts}/{MAX_FAILED_ATTEMPTS})")

    def purge_expired_sessions(self) -> int:
        """Suresi dolmus oturum satirlarini sil; silinen sayisini dondur.

        validate_token yalnizca DOKUNULAN token'i temizler; bir daha hic
        kullanilmayan oturumlar tabloda birikirdi. Acilista bir kez cagrilir.
        """
        with self.store._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE expires_at <= ?", (_now().isoformat(),)
            )
            conn.commit()
            return cursor.rowcount

    def validate_token(self, token: str) -> Optional[dict]:
        """Token'i kullaniciya cozumle. Gecersiz/suresi dolmussa None."""
        if not token:
            return None

        with self.store._connect() as conn:
            row = conn.execute(
                """SELECT s.expires_at, u.*
                   FROM sessions s JOIN users u ON u.id = s.user_id
                   WHERE s.token_hash = ?""",
                (_hash_token(token),)
            ).fetchone()

            if row is None:
                return None

            if datetime.fromisoformat(row["expires_at"]) <= _now():
                conn.execute("DELETE FROM sessions WHERE token_hash = ?",
                             (_hash_token(token),))
                conn.commit()
                return None

            if not row["is_active"]:
                return None

        return self._to_user_dict(row)

    def logout(self, token: str):
        if not token:
            return
        with self.store._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_hash_token(token),))
            conn.commit()

    # ------------------------------------------------------------ parola

    def _set_password(self, user_id: int, new_password: str, forced: bool):
        """Parolayi degistir ve kullanicinin TUM oturumlarini dusur.

        Oturumlarin dusurulmesi kritik: parola degistirilmesinin amaci
        genelde calinmis bir erisimi kesmektir.
        """
        self._validate_password(new_password)
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, must_change_password = ? WHERE id = ?",
                (hash_password(new_password), 1 if forced else 0, user_id)
            )
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()

    def change_password(self, user_id: int, old_password: str, new_password: str):
        """Kullanicinin kendi parolasini degistirmesi (eski parola gerekir)."""
        user_row = None
        with self.store._connect() as conn:
            user_row = conn.execute(
                "SELECT password_hash FROM users WHERE id = ?", (user_id,)
            ).fetchone()

        if user_row is None:
            raise ValueError("Kullanici bulunamadi")
        if not verify_password(old_password, user_row["password_hash"]):
            raise ValueError("Mevcut parola hatali")

        self._set_password(user_id, new_password, forced=False)
        self.log_action(user_id, "password_changed", None)

    def admin_reset_password(self, user_id: int, new_password: str):
        """Admin tarafindan sifirlama; kullanici ilk giriste degistirmek zorunda."""
        self._set_password(user_id, new_password, forced=True)
        self.log_action(user_id, "password_reset_by_admin", None)

    # ------------------------------------------------------------ kurulum

    def bootstrap_admin(self) -> Optional[tuple]:
        """Ilk kurulumda rastgele parolali admin olustur.

        Sabit varsayilan parola (admin/admin) ile teslim edilen sistem
        guvenlik acigidir. Uretilen parola cagirana dondurulur, konsola
        yazilir ve ilk giriste degistirilmesi zorunludur.

        Kullanici zaten varsa hicbir sey yapmaz (None doner).
        """
        with self.store._connect() as conn:
            count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
        if count > 0:
            return None

        password = secrets.token_urlsafe(12)
        self.create_user("admin", password, role="admin")
        logger.warning("Ilk kurulum: 'admin' hesabi olusturuldu")
        return ("admin", password)

    # ------------------------------------------------------------ denetim

    def _log(self, user_id, username, action, detail):
        with self.store._connect() as conn:
            conn.execute(
                "INSERT INTO audit_log (user_id, username, action, detail, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, username, action, detail, _now().isoformat())
            )
            conn.commit()

    def log_action(self, user_id: int, action: str, detail: Optional[str] = None):
        """Kullanici eylemini denetim kaydina yaz (or. sorulan soru)."""
        user = self.get_user(user_id) if user_id else None
        self._log(user_id, user["username"] if user else None, action, detail)

    def get_audit_log(self, limit: int = 100) -> List[dict]:
        with self.store._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
