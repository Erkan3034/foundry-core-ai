"""
Foundry RAG Assistant - Kimlik Dogrulama Testleri

Kullanici verileri knowledge_base.db'den AYRI bir dosyada (auth.db) tutulur:
- POST /reset bilgi tabanini siler, hesaplari silmemeli
- Bilgi tabani yedegi parola hash'i tasimamali
- Iki dosyaya ayri dosya izni verilebilir
"""

import time
import pytest

from auth import AuthService, AuthStore


@pytest.fixture
def auth(tmp_path):
    store = AuthStore(db_path=str(tmp_path / "auth.db"))
    return AuthService(store)


@pytest.fixture
def admin(auth):
    return auth.create_user("patron", "AdminParola123", role="admin")


class TestUserCreation:

    def test_creates_user(self, auth):
        user = auth.create_user("ayse", "Parola123", role="user")
        assert user["username"] == "ayse"
        assert user["role"] == "user"
        assert user["is_active"] is True

    def test_password_is_not_stored_in_plaintext(self, auth, tmp_path):
        auth.create_user("ayse", "GizliParola123")
        with auth.store._connect() as conn:
            row = conn.execute("SELECT password_hash FROM users").fetchone()
        assert "GizliParola123" not in row["password_hash"]
        assert row["password_hash"].startswith("scrypt$")

    def test_new_user_must_change_password(self, auth):
        """Admin'in verdigi parola ilk giriste degistirilmeli."""
        user = auth.create_user("ayse", "GeciciParola1")
        assert user["must_change_password"] is True

    def test_duplicate_username_rejected(self, auth):
        auth.create_user("ayse", "Parola123")
        with pytest.raises(ValueError, match="zaten"):
            auth.create_user("ayse", "BaskaParola123")

    def test_username_is_case_insensitive(self, auth):
        """'Ayse' ve 'ayse' ayni hesap olmali; aksi halde kafa karisikligi."""
        auth.create_user("Ayse", "Parola123")
        with pytest.raises(ValueError):
            auth.create_user("ayse", "Parola123")

    def test_rejects_empty_username(self, auth):
        with pytest.raises(ValueError):
            auth.create_user("", "Parola123")

    def test_rejects_short_password(self, auth):
        with pytest.raises(ValueError, match="karakter"):
            auth.create_user("ayse", "kisa")

    def test_rejects_invalid_role(self, auth):
        with pytest.raises(ValueError):
            auth.create_user("ayse", "Parola123", role="superuser")


class TestAuthentication:

    def test_correct_password_returns_token(self, auth):
        auth.create_user("ayse", "Parola123")
        token = auth.authenticate("ayse", "Parola123")
        assert token is not None
        assert len(token) >= 32

    def test_wrong_password_returns_none(self, auth):
        auth.create_user("ayse", "Parola123")
        assert auth.authenticate("ayse", "YanlisParola") is None

    def test_unknown_user_returns_none(self, auth):
        assert auth.authenticate("yokboyle", "Parola123") is None

    def test_inactive_user_cannot_login(self, auth):
        user = auth.create_user("ayse", "Parola123")
        auth.deactivate_user(user["id"])
        assert auth.authenticate("ayse", "Parola123") is None

    def test_login_is_case_insensitive_on_username(self, auth):
        auth.create_user("ayse", "Parola123")
        assert auth.authenticate("AYSE", "Parola123") is not None

    def test_token_is_stored_hashed(self, auth):
        """DB sizarsa token'lar dogrudan kullanilamamali."""
        auth.create_user("ayse", "Parola123")
        token = auth.authenticate("ayse", "Parola123")
        with auth.store._connect() as conn:
            rows = [dict(r) for r in conn.execute("SELECT * FROM sessions")]
        assert all(token not in str(r.values()) for r in rows)


class TestSessions:

    def test_valid_token_resolves_to_user(self, auth):
        auth.create_user("ayse", "Parola123")
        token = auth.authenticate("ayse", "Parola123")
        user = auth.validate_token(token)
        assert user["username"] == "ayse"

    def test_invalid_token_returns_none(self, auth):
        assert auth.validate_token("uydurma-token") is None
        assert auth.validate_token("") is None
        assert auth.validate_token(None) is None

    def test_expired_token_rejected(self, auth):
        auth.create_user("ayse", "Parola123")
        token = auth.authenticate("ayse", "Parola123", ttl_seconds=1)
        assert auth.validate_token(token) is not None
        time.sleep(1.1)
        assert auth.validate_token(token) is None

    def test_logout_invalidates_token(self, auth):
        auth.create_user("ayse", "Parola123")
        token = auth.authenticate("ayse", "Parola123")
        auth.logout(token)
        assert auth.validate_token(token) is None

    def test_deactivating_user_kills_active_sessions(self, auth):
        """Isten ayrilan calisanin oturumu ANINDA gecersiz olmali."""
        user = auth.create_user("ayse", "Parola123")
        token = auth.authenticate("ayse", "Parola123")
        auth.deactivate_user(user["id"])
        assert auth.validate_token(token) is None


class TestPasswordChange:

    def test_change_password_clears_forced_flag(self, auth):
        user = auth.create_user("ayse", "GeciciParola1")
        auth.change_password(user["id"], "GeciciParola1", "YeniParola456")
        assert auth.get_user(user["id"])["must_change_password"] is False

    def test_change_password_requires_correct_old_password(self, auth):
        user = auth.create_user("ayse", "GeciciParola1")
        with pytest.raises(ValueError):
            auth.change_password(user["id"], "YanlisEski", "YeniParola456")

    def test_can_login_with_new_password(self, auth):
        user = auth.create_user("ayse", "GeciciParola1")
        auth.change_password(user["id"], "GeciciParola1", "YeniParola456")
        assert auth.authenticate("ayse", "YeniParola456") is not None
        assert auth.authenticate("ayse", "GeciciParola1") is None

    def test_change_password_kills_other_sessions(self, auth):
        """Parola degisikligi calinmis oturumlari dusurmeli."""
        user = auth.create_user("ayse", "GeciciParola1")
        eski_token = auth.authenticate("ayse", "GeciciParola1")
        auth.change_password(user["id"], "GeciciParola1", "YeniParola456")
        assert auth.validate_token(eski_token) is None

    def test_new_password_must_meet_length_rule(self, auth):
        user = auth.create_user("ayse", "GeciciParola1")
        with pytest.raises(ValueError):
            auth.change_password(user["id"], "GeciciParola1", "kisa")


class TestAdminReset:
    """Kullanici parolasini unuttugunda admin sifirlayabilmeli."""

    def test_admin_reset_sets_new_password(self, auth, admin):
        user = auth.create_user("ayse", "EskiParola1")
        auth.admin_reset_password(user["id"], "SifirlananParola1")
        assert auth.authenticate("ayse", "SifirlananParola1") is not None

    def test_admin_reset_forces_change_on_next_login(self, auth, admin):
        user = auth.create_user("ayse", "EskiParola1")
        auth.change_password(user["id"], "EskiParola1", "KendiParolam1")
        auth.admin_reset_password(user["id"], "SifirlananParola1")
        assert auth.get_user(user["id"])["must_change_password"] is True

    def test_admin_reset_kills_sessions(self, auth, admin):
        user = auth.create_user("ayse", "EskiParola1")
        token = auth.authenticate("ayse", "EskiParola1")
        auth.admin_reset_password(user["id"], "SifirlananParola1")
        assert auth.validate_token(token) is None


class TestBootstrap:
    """Teslim kurulumu: sabit varsayilan parola ILE TESLIM EDILMEZ."""

    def test_bootstrap_creates_admin_with_random_password(self, auth):
        username, password = auth.bootstrap_admin()
        assert username
        assert len(password) >= 12
        assert auth.authenticate(username, password) is not None

    def test_bootstrap_password_is_random(self, tmp_path):
        a = AuthService(AuthStore(db_path=str(tmp_path / "a.db"))).bootstrap_admin()
        b = AuthService(AuthStore(db_path=str(tmp_path / "b.db"))).bootstrap_admin()
        assert a[1] != b[1], "her kurulum farkli parola uretmeli"

    def test_bootstrap_admin_must_change_password(self, auth):
        username, _ = auth.bootstrap_admin()
        user = auth.get_user_by_username(username)
        assert user["must_change_password"] is True

    def test_bootstrap_is_noop_when_users_exist(self, auth):
        auth.create_user("patron", "Parola123", role="admin")
        assert auth.bootstrap_admin() is None


class TestAuditLog:
    """Kullanici bazli girisin asil faydasi: kim neyi sordu."""

    def test_successful_login_is_logged(self, auth):
        auth.create_user("ayse", "Parola123")
        auth.authenticate("ayse", "Parola123")
        actions = [e["action"] for e in auth.get_audit_log()]
        assert "login" in actions

    def test_failed_login_is_logged(self, auth):
        auth.create_user("ayse", "Parola123")
        auth.authenticate("ayse", "YanlisParola")
        actions = [e["action"] for e in auth.get_audit_log()]
        assert "login_failed" in actions

    def test_query_can_be_logged_with_user(self, auth):
        user = auth.create_user("ayse", "Parola123")
        auth.log_action(user["id"], "query", "yillik izin kac gun")
        entry = auth.get_audit_log()[0]
        assert entry["username"] == "ayse"
        assert entry["detail"] == "yillik izin kac gun"


class TestStorageSeparation:

    def test_uses_separate_database_file(self, tmp_path):
        path = str(tmp_path / "auth.db")
        store = AuthStore(db_path=path)
        AuthService(store).create_user("ayse", "Parola123")
        import os
        assert os.path.exists(path)

    def test_knowledge_base_tables_absent(self, auth):
        """auth.db icinde belge/parca tablosu OLMAMALI."""
        with auth.store._connect() as conn:
            names = {r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
        assert "chunks" not in names
        assert "documents" not in names
        assert {"users", "sessions", "audit_log"} <= names


class TestBruteForceLockout:
    """Kaba kuvvet korumasi (Z3).

    scrypt tek basina yeterli fren degil; N basarisiz denemeden sonra hesap
    kisa sureligine kilitlenmeli.
    """

    def test_locks_account_after_repeated_failures(self, auth):
        from auth import MAX_FAILED_ATTEMPTS
        auth.create_user("ayse", "DogruParola123")

        for _ in range(MAX_FAILED_ATTEMPTS):
            assert auth.authenticate("ayse", "yanlis") is None

        # Kilitliyken DOGRU parola da reddedilmeli; aksi halde kilit
        # hicbir sey ifade etmezdi.
        assert auth.authenticate("ayse", "DogruParola123") is None

    def test_successful_login_resets_counter(self, auth):
        from auth import MAX_FAILED_ATTEMPTS
        auth.create_user("ayse", "DogruParola123")

        for _ in range(MAX_FAILED_ATTEMPTS - 1):
            auth.authenticate("ayse", "yanlis")

        # Esige ulasmadan basarili giris sayaci sifirlamali
        assert auth.authenticate("ayse", "DogruParola123") is not None

        for _ in range(MAX_FAILED_ATTEMPTS - 1):
            auth.authenticate("ayse", "yanlis")
        assert auth.authenticate("ayse", "DogruParola123") is not None

    def test_lock_expires_and_allows_login(self, auth, monkeypatch):
        import auth as auth_module
        from auth import MAX_FAILED_ATTEMPTS
        auth.create_user("ayse", "DogruParola123")

        # Kilit suresini olculebilir sekilde kisalt
        monkeypatch.setattr(auth_module, "LOCKOUT_SECONDS", -1)

        for _ in range(MAX_FAILED_ATTEMPTS):
            auth.authenticate("ayse", "yanlis")

        # Suresi gecmis kilit girisi engellememeli
        assert auth.authenticate("ayse", "DogruParola123") is not None

    def test_lockout_is_recorded_in_audit_log(self, auth):
        from auth import MAX_FAILED_ATTEMPTS
        auth.create_user("ayse", "DogruParola123")
        for _ in range(MAX_FAILED_ATTEMPTS):
            auth.authenticate("ayse", "yanlis")

        actions = [entry["action"] for entry in auth.get_audit_log()]
        assert "account_locked" in actions


class TestSessionPurge:
    """Suresi dolmus oturumlarin temizlenmesi (Z8)."""

    def test_purges_expired_sessions(self, auth):
        auth.create_user("ayse", "Parola123")
        expired = auth.authenticate("ayse", "Parola123", ttl_seconds=-1)
        assert expired is not None

        assert auth.purge_expired_sessions() >= 1
        assert auth.validate_token(expired) is None

    def test_keeps_live_sessions(self, auth):
        auth.create_user("ayse", "Parola123")
        live = auth.authenticate("ayse", "Parola123", ttl_seconds=3600)

        auth.purge_expired_sessions()
        assert auth.validate_token(live) is not None


class TestSchemaMigration:
    """Eski auth.db dosyalari veri kaybi olmadan guncellenmeli."""

    def test_migrates_old_schema_without_data_loss(self, tmp_path):
        import sqlite3
        db = str(tmp_path / "old.db")

        # Kilitleme kolonlari OLMAYAN eski sema
        conn = sqlite3.connect(db)
        conn.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1,
                must_change_password INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login_at TEXT
            );
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES ('eski_kullanici', 'hash', 'admin', '2026-01-01T00:00:00');
        """)
        conn.commit()
        conn.close()

        # AuthStore acilisi semayi tasimali
        service = AuthService(AuthStore(db_path=db))

        users = service.list_users()
        assert any(u["username"] == "eski_kullanici" for u in users)

        conn = sqlite3.connect(db)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(users)")}
        conn.close()
        assert "failed_attempts" in cols
        assert "locked_until" in cols
