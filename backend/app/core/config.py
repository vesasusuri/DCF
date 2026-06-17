import os
import ssl
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"

# asyncpg does not accept these URL query params as connect() kwargs.
_ASYNCPG_STRIPPED_QUERY_PARAMS = frozenset({"pgbouncer"})


def _resolve_supabase_anon_key() -> str:
    """Read anon key from .env when only VITE_SUPABASE_ANON_KEY is defined."""
    values = dotenv_values(ENV_FILE)
    return (values.get("SUPABASE_ANON_KEY") or values.get("VITE_SUPABASE_ANON_KEY") or "").strip()


def _to_asyncpg_scheme(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def _strip_asyncpg_query_params(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return url

    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in _ASYNCPG_STRIPPED_QUERY_PARAMS
    ]
    return urlunparse(parsed._replace(query=urlencode(query_pairs)))


def _uses_supabase_transaction_pooler(url: str) -> bool:
    normalized = url.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(normalized)
    query = (parsed.query or "").lower()
    return parsed.port == 6543 or "pgbouncer=true" in query


def _is_supabase_database_host(url: str) -> bool:
    normalized = url.replace("postgresql+asyncpg://", "postgresql://")
    hostname = urlparse(normalized).hostname or ""
    return "supabase.com" in hostname


def _supabase_ssl_context() -> ssl.SSLContext:
    """Supabase requires SSL; relax verification for local development on Windows."""
    context = ssl.create_default_context()
    if os.getenv("APP_ENV", "development") == "development":
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    api_prefix: str = "/api/v1"

    cors_origins: str = "http://localhost:5173"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "dcf-files"

    database_url: str = ""
    database_migration_url: str = ""
    direct_url: str = ""

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        origins: list[str] = []
        for value in (self.cors_origins, os.getenv("BACKEND_CORS_ORIGINS", "")):
            origins.extend(origin.strip() for origin in value.split(",") if origin.strip())
        # Preserve order while deduplicating.
        return list(dict.fromkeys(origins))

    @property
    def runtime_database_url(self) -> str:
        """Prefer direct/session connection for async ORM; pooler URL is a fallback."""
        return (self.direct_url or self.database_migration_url or self.database_url).strip()

    @property
    def sqlalchemy_url(self) -> str:
        url = self.runtime_database_url
        if not url:
            return ""
        return _strip_asyncpg_query_params(_to_asyncpg_scheme(url))

    @property
    def sqlalchemy_connect_args(self) -> dict[str, object]:
        url = self.runtime_database_url
        if not url:
            return {}

        connect_args: dict[str, object] = {}
        if _is_supabase_database_host(url):
            connect_args["ssl"] = _supabase_ssl_context()
        if _uses_supabase_transaction_pooler(url):
            # Required for Supabase transaction pooler (PgBouncer) with asyncpg.
            connect_args["statement_cache_size"] = 0
        return connect_args

    @property
    def alembic_url(self) -> str:
        url = (self.database_migration_url or self.direct_url or self.database_url).strip()
        if not url:
            return url
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url.split("?")[0]

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.supabase_anon_key:
        settings.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "") or _resolve_supabase_anon_key()
    return settings
