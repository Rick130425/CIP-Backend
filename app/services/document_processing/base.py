from abc import ABC, abstractmethod
from app.schemas.document_schema import DocumentConversionResult


class BaseDocumentExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> DocumentConversionResult:
        pass
