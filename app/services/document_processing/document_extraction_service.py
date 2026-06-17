from pathlib import Path
from app.schemas.document_schema import DocumentConversionResult
from app.services.document_processing.docx_extractor import DocxExtractor
from app.services.document_processing.pdf_extractor import PdfExtractor
from app.services.document_processing.txt_extractor import TxtExtractor


class DocumentExtractionService:
    def __init__(self) -> None:
        self.pdf_extractor = PdfExtractor()
        self.docx_extractor = DocxExtractor()
        self.txt_extractor = TxtExtractor()

    def extract(self, file_path: str) -> DocumentConversionResult:
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return self.pdf_extractor.extract(file_path)

        if extension == ".docx":
            return self.docx_extractor.extract(file_path)

        if extension == ".txt":
            return self.txt_extractor.extract(file_path)

        raise ValueError(f"Unsupported file type: {extension}")
