import asyncio
from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings
from app.domain.interfaces.file_storage import IFileStorage


@lru_cache
def get_supabase_client() -> Client | None:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


class SupabaseFileStorage(IFileStorage):
    def __init__(self, bucket: str | None = None) -> None:
        settings = get_settings()
        self._bucket = bucket or settings.supabase_storage_bucket
        self._client = get_supabase_client()

    def _require_client(self) -> Client:
        if self._client is None:
            raise RuntimeError(
                "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
        return self._client

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        client = self._require_client()

        def _upload() -> str:
            client.storage.from_(self._bucket).upload(
                path=key,
                file=data,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            return key

        return await asyncio.to_thread(_upload)

    async def download(self, key: str) -> bytes:
        client = self._require_client()

        def _download() -> bytes:
            return client.storage.from_(self._bucket).download(key)

        return await asyncio.to_thread(_download)

    async def delete(self, key: str) -> None:
        client = self._require_client()

        def _delete() -> None:
            client.storage.from_(self._bucket).remove([key])

        await asyncio.to_thread(_delete)

    async def get_url(self, key: str) -> str:
        client = self._require_client()

        def _url() -> str:
            return client.storage.from_(self._bucket).get_public_url(key)

        return await asyncio.to_thread(_url)
