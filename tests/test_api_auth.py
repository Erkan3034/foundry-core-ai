"""
Foundry RAG Assistant - Endpoint Yetkilendirme Testleri

Senaryo: sistem firmanin sunucusuna kurulur, sirket WiFi'sindeki herkes
adrese erisir. Bu yuzden AGA ERISIM = YETKI DEGILDIR; her endpoint kendi
yetkisini kontrol etmelidir.

Yetki seviyeleri:
  - herkese acik : /health, /auth/login
  - giris yapmis : /query, /documents (okuma)
  - admin        : /ingest/*, DELETE /documents, /reset, kullanici yonetimi
"""

import pytest
from fastapi.testclient import TestClient

import api_server
from api_server import app, get_auth_service
from auth import AuthStore, AuthService


@pytest.fixture
def service(tmp_path):
    return AuthService(AuthStore(db_path=str(tmp_path / "auth.db")))


@pytest.fixture
def client(service):
    app.dependency_overrides[get_auth_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def _login(client, username, password):
    r = client.post("/auth/login", json={"username": username, "password": password})
    return r.json().get("token") if r.status_code == 200 else None


@pytest.fixture
def admin_token(client, service):
    service.create_user("patron", "AdminParola1", role="admin")
    token = _login(client, "patron", "AdminParola1")
    # Ilk giriste parola degistirme zorunlulugunu gecelim
    client.post("/auth/change-password",
                json={"old_password": "AdminParola1", "new_password": "YeniAdmin123"},
                headers={"Authorization": f"Bearer {token}"})
    return _login(client, "patron", "YeniAdmin123")


@pytest.fixture
def user_token(client, service):
    service.create_user("ayse", "KullaniciParola1", role="user")
    token = _login(client, "ayse", "KullaniciParola1")
    client.post("/auth/change-password",
                json={"old_password": "KullaniciParola1", "new_password": "YeniKullanici1"},
                headers={"Authorization": f"Bearer {token}"})
    return _login(client, "ayse", "YeniKullanici1")


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _call(client, method, path, token=None):
    """GET/DELETE json govde kabul etmez; metoda gore cagri kur."""
    headers = _auth(token) if token else {}
    if method in ("post", "put", "patch"):
        return getattr(client, method)(path, json={}, headers=headers)
    return getattr(client, method)(path, headers=headers)


# ---------------------------------------------------------------- acik uclar

class TestPublicEndpoints:

    def test_health_is_public(self, client):
        """Izleme/monitoring icin acik kalmali."""
        assert client.get("/health").status_code == 200

    def test_login_is_public(self, client, service):
        service.create_user("ayse", "Parola123")
        r = client.post("/auth/login", json={"username": "ayse", "password": "Parola123"})
        assert r.status_code == 200
        assert "token" in r.json()

    def test_login_with_wrong_password_returns_401(self, client, service):
        service.create_user("ayse", "Parola123")
        r = client.post("/auth/login", json={"username": "ayse", "password": "Yanlis"})
        assert r.status_code == 401

    def test_login_does_not_leak_user_existence(self, client, service):
        """Olmayan kullanici ile yanlis parola AYNI yaniti vermeli."""
        service.create_user("ayse", "Parola123")
        a = client.post("/auth/login", json={"username": "ayse", "password": "Yanlis"})
        b = client.post("/auth/login", json={"username": "yokboyle", "password": "Yanlis"})
        assert a.status_code == b.status_code == 401
        assert a.json()["detail"] == b.json()["detail"]


# ------------------------------------------------------- giris zorunlulugu

class TestAuthenticationRequired:

    @pytest.mark.parametrize("method,path", [
        ("post", "/query"),
        ("post", "/query/stream"),
        ("get", "/documents"),
        ("get", "/stats"),
        ("post", "/ingest/directory"),
        ("delete", "/documents/1"),
        ("post", "/reset"),
    ])
    def test_rejects_anonymous(self, client, method, path):
        r = _call(client, method, path)
        assert r.status_code == 401, f"{method.upper()} {path} anonim erisime acik!"

    def test_rejects_invalid_token(self, client):
        r = client.get("/documents", headers=_auth("uydurma-token"))
        assert r.status_code == 401

    def test_rejects_logged_out_token(self, client, user_token):
        client.post("/auth/logout", headers=_auth(user_token))
        assert client.get("/documents", headers=_auth(user_token)).status_code == 401


# --------------------------------------------------------------- rol ayrimi

class TestRoleSeparation:

    @pytest.mark.parametrize("method,path", [
        ("post", "/ingest/directory"),
        ("delete", "/documents/1"),
        ("post", "/reset"),
        ("get", "/auth/users"),
    ])
    def test_regular_user_forbidden_on_admin_endpoints(self, client, user_token, method, path):
        r = _call(client, method, path, token=user_token)
        assert r.status_code == 403, f"{method.upper()} {path} normal kullaniciya acik!"

    def test_admin_allowed_on_admin_endpoints(self, client, admin_token):
        r = client.get("/auth/users", headers=_auth(admin_token))
        assert r.status_code == 200

    def test_regular_user_can_query(self, client, user_token):
        """401/403 OLMAMALI. RAG motoru testte yuklu degil, 503 kabul."""
        r = client.post("/query", json={"query": "test"}, headers=_auth(user_token))
        assert r.status_code not in (401, 403)

    def test_regular_user_can_list_documents(self, client, user_token):
        assert client.get("/documents", headers=_auth(user_token)).status_code == 200


# ------------------------------------------------- ilk giriste parola degisimi

class TestForcedPasswordChange:

    def test_new_user_blocked_until_password_changed(self, client, service):
        service.create_user("ayse", "GeciciParola1")
        token = _login(client, "ayse", "GeciciParola1")
        r = client.get("/documents", headers=_auth(token))
        assert r.status_code == 403
        assert "password_change_required" in str(r.json())

    def test_can_change_password_while_blocked(self, client, service):
        service.create_user("ayse", "GeciciParola1")
        token = _login(client, "ayse", "GeciciParola1")
        r = client.post("/auth/change-password",
                        json={"old_password": "GeciciParola1", "new_password": "YeniParola1"},
                        headers=_auth(token))
        assert r.status_code == 200

    def test_access_granted_after_change(self, client, user_token):
        assert client.get("/documents", headers=_auth(user_token)).status_code == 200


# ------------------------------------------------------- kullanici yonetimi

class TestUserManagement:

    def test_admin_creates_user(self, client, admin_token):
        r = client.post("/auth/users",
                        json={"username": "yeni", "password": "YeniParola1", "role": "user"},
                        headers=_auth(admin_token))
        assert r.status_code == 200
        assert r.json()["username"] == "yeni"

    def test_created_user_must_change_password(self, client, admin_token):
        r = client.post("/auth/users",
                        json={"username": "yeni", "password": "YeniParola1", "role": "user"},
                        headers=_auth(admin_token))
        assert r.json()["must_change_password"] is True

    def test_admin_resets_password(self, client, admin_token, service):
        user = service.create_user("ayse", "EskiParola1")
        r = client.post(f"/auth/users/{user['id']}/reset-password",
                        json={"new_password": "SifirlananP1"}, headers=_auth(admin_token))
        assert r.status_code == 200
        assert _login(client, "ayse", "SifirlananP1") is not None

    def test_admin_deactivates_user(self, client, admin_token, service):
        user = service.create_user("ayse", "Parola123")
        r = client.post(f"/auth/users/{user['id']}/deactivate", headers=_auth(admin_token))
        assert r.status_code == 200
        assert _login(client, "ayse", "Parola123") is None

    def test_duplicate_username_returns_400(self, client, admin_token):
        payload = {"username": "yeni", "password": "YeniParola1", "role": "user"}
        client.post("/auth/users", json=payload, headers=_auth(admin_token))
        r = client.post("/auth/users", json=payload, headers=_auth(admin_token))
        assert r.status_code == 400

    def test_weak_password_returns_400(self, client, admin_token):
        r = client.post("/auth/users",
                        json={"username": "yeni", "password": "kisa", "role": "user"},
                        headers=_auth(admin_token))
        assert r.status_code == 400


# ------------------------------------------------------------------ oturum

class TestSessionEndpoints:

    def test_me_returns_current_user(self, client, user_token):
        r = client.get("/auth/me", headers=_auth(user_token))
        assert r.status_code == 200
        body = r.json()
        assert body["username"] == "ayse"
        assert body["role"] == "user"

    def test_me_never_returns_password_hash(self, client, user_token):
        body = client.get("/auth/me", headers=_auth(user_token)).json()
        assert "password_hash" not in body
        assert "scrypt" not in str(body)

    def test_deactivated_user_token_stops_working(self, client, admin_token, service):
        service.create_user("ayse", "Parola1234")
        token = _login(client, "ayse", "Parola1234")
        user = service.get_user_by_username("ayse")
        client.post(f"/auth/users/{user['id']}/deactivate", headers=_auth(admin_token))
        assert client.get("/auth/me", headers=_auth(token)).status_code == 401


# --------------------------------------------------- bilgi sizintisi

class TestInformationDisclosure:
    """Kimlik dogrulamasi olmadan is bilgisi sizmamali."""

    def test_public_health_does_not_leak_stats(self, client):
        """Giris yapmamis biri kac belge oldugunu ogrenememeli.

        /health izleme icin acik kalmali ama yalnizca canlilik bilgisi
        vermeli; belge/parca sayilari is bilgisidir.
        """
        body = client.get("/health").json()
        assert "stats" not in body or not body["stats"], \
            f"/health istatistik sizdiriyor: {body.get('stats')}"

    def test_health_still_reports_liveness(self, client):
        body = client.get("/health").json()
        assert body["status"] == "healthy"
        assert "version" in body
        assert "database_ready" in body

    def test_stats_requires_admin(self, client, user_token):
        """Detayli istatistikler operasyonel bilgi; normal kullaniciya kapali."""
        r = client.get("/stats", headers=_auth(user_token))
        assert r.status_code == 403

    def test_admin_can_read_stats(self, client, admin_token):
        r = client.get("/stats", headers=_auth(admin_token))
        assert r.status_code == 200
        assert "chunks" in r.json()
