import logging
from app.storage.storage_interface import StorageInterface
from app.storage.local_storage import LocalStorage
from app.config.settings import settings

logger = logging.getLogger(__name__)


class SupabaseStorage(StorageInterface):
    def __init__(self):
        self.fallback = LocalStorage()
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY

    def save_file(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        if not self.supabase_url or not self.supabase_key:
            logger.info("Supabase credentials not configured. Falling back to LocalStorage.")
            return self.fallback.save_file(file_bytes, filename, content_type)

        try:
            # Here real Supabase storage SDK upload can be invoked
            # e.g., supabase.storage.from_("artisan-assets").upload(...)
            return self.fallback.save_file(file_bytes, filename, content_type)
        except Exception as e:
            logger.error(f"Supabase storage upload failed: {e}. Falling back to local storage.")
            return self.fallback.save_file(file_bytes, filename, content_type)

    def read_file(self, file_url: str) -> bytes:
        return self.fallback.read_file(file_url)

    def delete_file(self, file_url: str) -> bool:
        return self.fallback.delete_file(file_url)


def get_storage_service() -> StorageInterface:
    if settings.STORAGE_BACKEND.lower() == "supabase":
        return SupabaseStorage()
    return LocalStorage()
