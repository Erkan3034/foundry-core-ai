"""
Foundry RAG Assistant - Configuration Module
Merkezi yapılandırma yönetimi. Tüm ayarlar buradan kontrol edilir.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


@dataclass(frozen=True)
class Config:
    """Uygulama yapılandırması. Immutable (değiştirilemez) yapı."""

    # Model Ayarları
    embedding_model_alias: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL_ALIAS", "qwen3-embedding-0.6b"))
    chat_model_alias: str = field(default_factory=lambda: os.getenv("CHAT_MODEL_ALIAS", "qwen2.5-1.5b"))

    # Cihaz secimi: "auto" varsayilan varyanti kullanir; "generic-cpu",
    # "cuda-gpu" gibi bir deger, id'sinde bu ifadeyi iceren varyanti secer.
    # Dusuk VRAM'li sistemlerde embedding'i CPU'da tutmak chat modeline yer acar.
    embedding_device: str = field(default_factory=lambda: os.getenv("EMBEDDING_DEVICE", "generic-cpu"))
    chat_device: str = field(default_factory=lambda: os.getenv("CHAT_DEVICE", "auto"))

    # Veritabanı
    database_path: str = field(default_factory=lambda: os.getenv("DATABASE_PATH", "knowledge_base.db"))

    # Uygulama
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "foundry-rag-assistant"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "info"))

    # Web Sunucu
    # GUVENLIK: varsayilan 127.0.0.1 - servis yalnizca bu makineden erisilir.
    # Firma sunucusuna kurup ag icinden erisim isteniyorsa API_HOST=0.0.0.0
    # BILINCLI olarak set edilmeli (ve onunde TLS sonlandiran bir ters vekil
    # olmali; duz HTTP'de parolalar ve oturum token'lari agda acik gider).
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "127.0.0.1"))

    # Kimlik dogrulama veritabani - bilgi tabanindan AYRI dosya.
    # /reset bilgi tabanini siler ama hesaplari silmemeli.
    auth_db_path: str = field(default_factory=lambda: os.getenv("AUTH_DB_PATH", "auth.db"))
    session_ttl_hours: int = field(default_factory=lambda: int(os.getenv("SESSION_TTL_HOURS", "12")))
    # Tarayici erisimine izin verilen kaynaklar. Ayni origin'den sunuldugu icin
    # varsayilan bostur; farkli bir domainden erisim gerekirse buraya eklenir.
    cors_origins: str = field(default_factory=lambda: os.getenv("CORS_ORIGINS", ""))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))

    # RAG Parametreleri
    top_k_retrieval: int = field(default_factory=lambda: int(os.getenv("TOP_K_RETRIEVAL", "3")))
    min_similarity: float = field(default_factory=lambda: float(os.getenv("MIN_SIMILARITY", "0.35")))
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200")))
    max_context_length: int = field(default_factory=lambda: int(os.getenv("MAX_CONTEXT_LENGTH", "4000")))

    # Hibrit arama (dense embedding + BM25 anahtar kelime)
    # Turkce'de dense arama morfolojide zayiflar ("izin" vs "izinleri");
    # BM25 on-ek eslesmesiyle telafi eder.
    use_hybrid_search: bool = field(
        default_factory=lambda: os.getenv("USE_HYBRID_SEARCH", "true").lower() == "true")
    # Fuzyon havuzu = top_k * bu carpan (siralamanin degisebilmesi icin genis tutulur)
    hybrid_pool_factor: int = field(
        default_factory=lambda: int(os.getenv("HYBRID_POOL_FACTOR", "5")))
    # Anahtar kelime eslesen parcalar icin gevsetilmis esik carpani.
    # 1.0 = gevsetme yok. Cok dusuk deger alakasiz cevaplara yol acar.
    keyword_rescue_ratio: float = field(
        default_factory=lambda: float(os.getenv("KEYWORD_RESCUE_RATIO", "0.75")))

    # LLM ornekleme
    max_tokens: int = field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "1024")))
    temperature: float = field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.35")))
    frequency_penalty: float = field(default_factory=lambda: float(os.getenv("FREQUENCY_PENALTY", "0.0")))

    # Model Cache
    model_cache_dir: str | None = field(default_factory=lambda: os.getenv("MODEL_CACHE_DIR"))

    # Belgeler
    documents_dir: str = "documents"

    @property
    def db_path(self) -> Path:
        """Veritabanı dosya yolu."""
        return Path(self.database_path)

    @property
    def docs_path(self) -> Path:
        """Belgeler dizini yolu."""
        return Path(self.documents_dir)


# Singleton instance
CONFIG = Config()
