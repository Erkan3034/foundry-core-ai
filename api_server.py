"""
Foundry RAG Assistant - API Server
FastAPI tabanli REST API. Sirket ici kullanim icin.
"""

import os
import sys
import json
import logging
import tempfile
from contextlib import asynccontextmanager
from typing import Optional

from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from config import CONFIG
from database import db
from ingestion import DocumentIngestor
from rag_engine import RAGEngine
from auth import AuthStore, AuthService


# Logging ayarlari
logging.basicConfig(
    level=getattr(logging, CONFIG.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global RAG Engine instance
rag_engine: Optional[RAGEngine] = None


# ============== Pydantic Models ==============

class QueryRequest(BaseModel):
    """Soru sorma istegi."""
    query: str = Field(..., min_length=1, max_length=2000, description="Kullanici sorusu")
    stream: bool = Field(default=False, description="Streaming yanit iste")


class QueryResponse(BaseModel):
    """Soru cevabi."""
    query: str
    answer: str
    sources: list[str]
    retrieved_chunks: int
    confidence: float
    status: str = "success"


class IngestResponse(BaseModel):
    """Ingestion sonucu."""
    status: str
    message: str
    stats: dict


class HealthResponse(BaseModel):
    """Saglik kontrolu."""
    status: str
    version: str
    models_loaded: bool
    database_ready: bool
    stats: dict


# ============== FastAPI App ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yasam dongusu yonetimi."""
    global rag_engine

    logger.info("API sunucusu baslatiliyor...")

    # Ilk kurulum: hic kullanici yoksa rastgele parolali admin olustur.
    # Sabit varsayilan parola (admin/admin) ile teslim GUVENLIK ACIGIDIR.
    bootstrap = _auth_service.bootstrap_admin()
    if bootstrap:
        username, password = bootstrap
        banner = "=" * 64
        logger.warning(
            f"\n{banner}\n"
            f"  ILK KURULUM - YONETICI HESABI OLUSTURULDU\n"
            f"{banner}\n"
            f"  Kullanici : {username}\n"
            f"  Parola    : {password}\n"
            f"{banner}\n"
            f"  BU PAROLA BIR DAHA GOSTERILMEYECEK. Simdi kaydedin.\n"
            f"  Ilk giriste degistirmeniz zorunludur.\n"
            f"{banner}"
        )

    if CONFIG.api_host == "0.0.0.0":
        logger.warning(
            "API_HOST=0.0.0.0 - servis TUM ag arayuzlerine acik. "
            "Duz HTTP uzerinde parolalar ve oturum token'lari agda ACIK METIN gider; "
            "onune TLS sonlandiran bir ters vekil (nginx/Caddy) koyun."
        )

    # RAG Engine'i baslat
    rag_engine = RAGEngine()
    try:
        rag_engine.initialize()
        logger.info("RAG Engine hazir")
    except Exception as e:
        logger.error(f"RAG Engine baslatma hatasi: {e}")
        rag_engine = None

    yield
    # Kapatma
    logger.info("Sunucu kapatiliyor...")
    if rag_engine:
        rag_engine.shutdown()


app = FastAPI(
    title="Foundry RAG Assistant API",
    description="Yerel belgeleriniz uzerinde soru-cevap yapan AI asistani",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Web UI ayni origin'den sunuldugu icin yalnizca yerel gelistirme
# adreslerine izin verilir. Farkli bir domainden erisim gerekirse buraya ekleyin.
_origins = [o.strip() for o in CONFIG.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"] + allow_credentials=True gecersiz bir kombinasyondur;
    # tarayicilar zaten reddeder. Varsayilan olarak capraz-origin kapali.
    allow_origins=_origins,
    allow_credentials=bool(_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Kimlik Dogrulama ==============

_auth_service = AuthService(AuthStore(CONFIG.auth_db_path))
# auto_error=False: eksik header'da FastAPI'nin kendi 403'u yerine
# bizim 401'imiz donsun (dogru semantik: kimlik yok = 401).
_bearer = HTTPBearer(auto_error=False)


def get_auth_service() -> AuthService:
    """Testlerde dependency_overrides ile degistirilebilsin diye ayri."""
    return _auth_service


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    """Giris yapmis kullaniciyi dondur; yoksa 401.

    NOT: aga erisim yetki DEGILDIR. Sistem sirket sunucusunda calisir ve
    WiFi'deki herkes adrese ulasir; her endpoint kendi yetkisini dogrular.
    """
    token = credentials.credentials if credentials else None
    user = auth.validate_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Giris gerekli")
    return user


def require_user(user: dict = Depends(get_current_user)) -> dict:
    """Girisi dogrula VE ilk giris parola degisiminin yapilmis olmasini sart kos."""
    if user["must_change_password"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "password_change_required",
                    "message": "Devam etmeden once parolanizi degistirmelisiniz"},
        )
    return user


def require_admin(user: dict = Depends(require_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Bu islem icin yonetici yetkisi gerekli")
    return user


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


class ResetPasswordRequest(BaseModel):
    new_password: str


@app.post("/auth/login")
async def login(request: LoginRequest, auth: AuthService = Depends(get_auth_service)):
    token = await run_in_threadpool(
        auth.authenticate, request.username, request.password,
        CONFIG.session_ttl_hours * 3600
    )
    if token is None:
        # Kullanici yok / parola yanlis AYNI mesaji dondurur: aksi halde
        # saldirgan hangi kullanici adlarinin kayitli oldugunu ogrenir.
        raise HTTPException(status_code=401, detail="Kullanici adi veya parola hatali")

    user = auth.validate_token(token)
    return {"token": token, "user": user}


@app.post("/auth/logout")
async def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
                 auth: AuthService = Depends(get_auth_service)):
    if credentials:
        auth.logout(credentials.credentials)
    return {"status": "ok"}


@app.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    """Mevcut oturum bilgisi. Parola degisimi bekleyen kullanici da erisebilir
    (arayuz hangi ekrani gosterecegini buradan ogrenir)."""
    return user


@app.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest,
                          user: dict = Depends(get_current_user),
                          auth: AuthService = Depends(get_auth_service)):
    """Parola degisimi require_user DEGIL get_current_user kullanir:
    zorunlu degisim bekleyen kullanicinin bunu yapabilmesi gerekir."""
    try:
        await run_in_threadpool(auth.change_password, user["id"],
                                request.old_password, request.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", "message": "Parola guncellendi, tekrar giris yapin"}


@app.get("/auth/users")
async def list_users(_: dict = Depends(require_admin),
                     auth: AuthService = Depends(get_auth_service)):
    return auth.list_users()


@app.post("/auth/users")
async def create_user(request: CreateUserRequest,
                      admin: dict = Depends(require_admin),
                      auth: AuthService = Depends(get_auth_service)):
    try:
        user = await run_in_threadpool(auth.create_user, request.username,
                                       request.password, request.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    auth.log_action(admin["id"], "user_created", request.username)
    return user


@app.post("/auth/users/{user_id}/reset-password")
async def reset_password(user_id: int, request: ResetPasswordRequest,
                         admin: dict = Depends(require_admin),
                         auth: AuthService = Depends(get_auth_service)):
    try:
        await run_in_threadpool(auth.admin_reset_password, user_id, request.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    auth.log_action(admin["id"], "password_reset", f"user_id={user_id}")
    return {"status": "ok"}


@app.post("/auth/users/{user_id}/deactivate")
async def deactivate_user(user_id: int,
                          admin: dict = Depends(require_admin),
                          auth: AuthService = Depends(get_auth_service)):
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Kendi hesabinizi kapatamazsiniz")
    auth.deactivate_user(user_id)
    return {"status": "ok"}


@app.get("/auth/audit-log")
async def audit_log(limit: int = 100, _: dict = Depends(require_admin),
                    auth: AuthService = Depends(get_auth_service)):
    return auth.get_audit_log(limit=limit)


# ============== Endpoints ==============

@app.get("/health", response_model=HealthResponse)
async def health():
    """Saglik kontrolu endpoint'i.

    Not: "/" rotasi bilerek tanimlanmadi; kok adres StaticFiles mount'una
    duser ve web arayuzunu (index.html) sunar.
    """
    # DIKKAT: bu endpoint kimlik dogrulamasi ISTEMEZ (izleme/monitoring icin).
    # Bu yuzden yalnizca canlilik bilgisi doner. Belge/parca sayilari is
    # bilgisidir ve giris yapmamis birine gosterilmez -> /stats (admin).
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded=rag_engine is not None and rag_engine._initialized,
        database_ready=True,
        stats={}
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, user: dict = Depends(require_user)):
    """Soru sor ve cevap al."""
    if not rag_engine or not rag_engine._initialized:
        raise HTTPException(status_code=503, detail="RAG Engine henuz hazir degil")

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Soru bos olamaz")

    # Denetim kaydi: kim neyi sordu. Kullanici bazli girisin asil faydasi bu
    # ve KVKK acisindan da savunulabilir olmasini saglar.
    _auth_service.log_action(user["id"], "query", request.query[:500])

    try:
        if request.stream:
            return StreamingResponse(
                rag_engine.answer_stream(request.query),
                media_type="text/event-stream"
            )

        # Normal yanit — bloklayan LLM cagrisini threadpool'da calistir ki
        # event loop (saglik kontrolu, statik dosyalar, UI) donmasin
        result = await run_in_threadpool(rag_engine.answer, request.query)
        return QueryResponse(**result)

    except Exception as e:
        logger.error(f"Sorgu hatasi: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/stream")
async def query_stream(request: QueryRequest, user: dict = Depends(require_user)):
    """Streaming soru-cevap (SSE)."""
    if not rag_engine or not rag_engine._initialized:
        raise HTTPException(status_code=503, detail="RAG Engine henuz hazir degil")

    _auth_service.log_action(user["id"], "query", request.query[:500])

    def event_generator():
        # Senkron generator: StreamingResponse bunu threadpool'da calistirir,
        # boylece her token uretildigi anda istemciye akar. (async sarmalayici
        # icindeki senkron dongu event loop'u bloke edip tum yaniti sona biriktirir.)
        try:
            yield from rag_engine.answer_stream(request.query)
        except Exception as e:
            logger.error(f"Streaming hatasi: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


def _get_ingestor() -> tuple[DocumentIngestor, bool]:
    """Ingestor olustur. Calisan engine varsa embedding modelini paylas.

    Ayri bir EmbeddingManager kurup shutdown etmek, ayni modeli kullanan
    RAG engine'in modelini de bellekten kaldiracagi icin paylasilan
    manager'a dokunulmaz. Donen bool: model paylasildi mi?
    """
    ingestor = DocumentIngestor()
    if rag_engine and rag_engine._initialized:
        ingestor.embedding_manager = rag_engine.retriever.embedding_manager
        return ingestor, True
    ingestor.embedding_manager.initialize()
    return ingestor, False


@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...), user: dict = Depends(require_admin)):
    """Dosya yukle ve isle."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in DocumentIngestor.SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen dosya formati: {suffix or 'uzantisiz'}")

    save_path = None
    try:
        # Dosyayi permanent olarak documents/ klasorune kaydet
        save_dir = CONFIG.docs_path
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / file.filename

        content = await file.read()
        save_path.write_bytes(content)

        ingestor, shared = _get_ingestor()
        try:
            result = ingestor.ingest_file(save_path, source_name=file.filename, force=True)
        finally:
            if not shared:
                ingestor.shutdown()

        stats = db.get_stats()
        return IngestResponse(
            status="success",
            message=f"{file.filename} basariyla islendi ve documents/ dizinine eklendi ({result['chunks']} parca)",
            stats=stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dosya yukleme hatasi: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _ingest_directory_task():
    """Arka plan gorevi: belgeler dizinini isle."""
    ingestor, shared = _get_ingestor()
    try:
        results = ingestor.ingest_directory(CONFIG.docs_path)
        success = sum(1 for r in results if r.get("status") == "success")
        logger.info(f"Dizin ingestion tamamlandi: {success}/{len(results)} basarili")
    except Exception as e:
        logger.error(f"Dizin ingestion hatasi: {e}")
    finally:
        if not shared:
            ingestor.shutdown()


@app.post("/ingest/directory")
async def ingest_directory(background_tasks: BackgroundTasks, user: dict = Depends(require_admin)):
    """Belgeler dizinini tara ve isle."""
    try:
        background_tasks.add_task(_ingest_directory_task)

        return IngestResponse(
            status="processing",
            message=f"{CONFIG.docs_path} dizini arka planda isleniyor...",
            stats=db.get_stats()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents(user: dict = Depends(require_user)):
    """Yuklenen belgeleri listele."""
    return {"documents": db.list_documents()}


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, user: dict = Depends(require_admin)):
    """Belge sil."""
    success = db.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Belge bulunamadi")
    return {"status": "success", "message": f"Belge {doc_id} silindi"}


@app.get("/stats")
async def get_stats(user: dict = Depends(require_admin)):
    """Veritabani istatistikleri."""
    return db.get_stats()


@app.post("/reset")
async def reset_database(confirm: bool = False, user: dict = Depends(require_admin)):
    """Tum verileri temizle. DIKKAT! confirm=true parametresi zorunludur."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Tum veriler silinecek. Onaylamak icin ?confirm=true parametresi ekleyin."
        )
    db.clear_all()
    return {"status": "success", "message": "Veritabani temizlendi"}


# ============== Web UI (static files, catch-all) ==============

web_ui_path = Path(__file__).parent / "web_ui"
if web_ui_path.exists():
    app.mount("/", StaticFiles(directory=str(web_ui_path), html=True), name="web_ui")
    logger.info(f"Web UI: http://localhost:{CONFIG.api_port}/")


# ============== Main ==============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host=CONFIG.api_host,
        port=CONFIG.api_port,
        reload=False,
        log_level=CONFIG.log_level
    )
