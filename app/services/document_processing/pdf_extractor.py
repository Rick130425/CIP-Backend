from langchain_pymupdf4llm import PyMuPDF4LLMLoader

from app.schemas.document_schema import DocumentConversionResult, DocumentUnit
from app.services.document_processing.base import BaseDocumentExtractor
from app.services.markdown_normalization_service import MarkdownNormalizationService


class PdfExtractor(BaseDocumentExtractor):
    def __init__(self) -> None:
        self.normalizer = MarkdownNormalizationService()

    def extract(self, file_path: str) -> DocumentConversionResult:
        loader = PyMuPDF4LLMLoader(
            file_path,
            mode="page",
            table_strategy="lines",
        )

        docs = loader.load()

        units: list[DocumentUnit] = []
        markdown_parts: list[str] = []

        for doc in docs:
            raw_content = doc.page_content or ""
            content = self.normalizer.normalize(raw_content)

            if not content:
                continue

            raw_page = doc.metadata.get("page")
            page_number = raw_page + 1 if isinstance(raw_page, int) else None

            units.append(
                DocumentUnit(
                    content=content,
                    page_number=page_number,
                )
            )

            if page_number is not None:
                markdown_parts.append(f"\n\n<!-- PAGE {page_number} -->\n\n{content}")
            else:
                markdown_parts.append(content)

        full_markdown = self.normalizer.normalize("\n\n".join(markdown_parts))

        if len(full_markdown) < 100:
            raise ValueError(
                "No extractable text found in PDF. "
                "Scanned PDFs are not supported in the MVP."
            )

        return DocumentConversionResult(
            full_markdown=full_markdown,
            units=units,
            source_type="pdf",
            extraction_engine="pymupdf4llm",
        )
