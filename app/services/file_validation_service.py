from pathlib import Path
from fastapi import UploadFile
from app.config import settings


class FileValidationService:
    allowed_extensions = {".pdf", ".docx", ".txt"}

    async def validate(self, file: UploadFile) -> bytes:
        if not file.filename:
            raise ValueError("Missing filename.")

        extension = Path(file.filename).suffix.lower()

        if extension not in self.allowed_extensions:
            raise ValueError(
                f"Unsupported file type '{extension}'. "
                "Only PDF, DOCX and TXT files are supported."
            )

        max_bytes = settings.max_upload_size_mb * 1024 * 1024

        accumulated_bytes = bytearray()
        chunk_size = 1024 * 1024  # 1 MB

        while chunk := await file.read(chunk_size):
            if len(accumulated_bytes) + len(chunk) > max_bytes:
                await file.close()
                raise ValueError(
                    f"File too large. Max size is {settings.max_upload_size_mb} MB."
                )

            accumulated_bytes.extend(chunk)

        if not accumulated_bytes:
            raise ValueError("Uploaded file is empty.")

        # Reset the file pointer to the beginning in case another service
        # needs to read from the UploadFile object again
        await file.seek(0)

        return bytes(accumulated_bytes)
