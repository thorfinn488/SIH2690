import os
import uuid
from app.storage.storage_interface import StorageInterface
from app.config.settings import settings


class LocalStorage(StorageInterface):
    def __init__(self, upload_dir: str = None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(self.upload_dir, unique_name)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Return static / local URL path
        return f"/static/uploads/{unique_name}"

    def read_file(self, file_url: str) -> bytes:
        filename = os.path.basename(file_url)
        file_path = os.path.join(self.upload_dir, filename)
        with open(file_path, "rb") as file_handle:
            return file_handle.read()

    def delete_file(self, file_url: str) -> bool:
        filename = os.path.basename(file_url)
        file_path = os.path.join(self.upload_dir, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False
        return False
