import re
from pathlib import Path
from uuid import uuid4

from app.config import settings


class FileStorageService:
    def __init__(self) -> None:
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, original_filename: str, content: bytes) -> tuple[str, str]:
        safe_name = self._sanitize_filename(original_filename)
        extension = Path(safe_name).suffix.lower()

        stored_filename = f"{uuid4().hex}{extension}"
        stored_path = self.upload_dir / stored_filename

        stored_path.write_bytes(content)

        return stored_filename, str(stored_path)

    def _sanitize_filename(self, filename: str) -> str:
        filename = filename.strip().replace(" ", "_")
        filename = re.sub(r"[^a-zA-Z0-9_.-]", "", filename)

        if not filename:
            return "uploaded_contract"

        return filename
