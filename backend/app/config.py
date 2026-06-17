from functools import lru_cache
from pathlib import Path
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"


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

    database_url: str = ""
    database_migration_url: str = ""
    direct_url: str = ""

    app_public_url: str = "http://localhost:8080"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.supabase_anon_key:
        settings.supabase_anon_key = os.getenv("VITE_SUPABASE_ANON_KEY", "")
    if not settings.smtp_user:
        settings.smtp_user = os.getenv("SMTP_USERNAME", "")
    if not settings.smtp_from:
        settings.smtp_from = os.getenv("SMTP_FROM_EMAIL", "")
    return settings
