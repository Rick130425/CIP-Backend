from docling.document_converter import DocumentConverter

from app.schemas.document_schema import DocumentConversionResult, DocumentUnit
from app.services.document_processing.base import BaseDocumentExtractor
from app.services.markdown_normalization_service import MarkdownNormalizationService


class DocxExtractor(BaseDocumentExtractor):
    def __init__(self) -> None:
        self.normalizer = MarkdownNormalizationService()
        self.converter = DocumentConverter()

    def extract(self, file_path: str) -> DocumentConversionResult:
        result = self.converter.convert(file_path)

        markdown = result.document.export_to_markdown()
        markdown = self.normalizer.normalize(markdown)

        if len(markdown) < 100:
            raise ValueError("No extractable text found in DOCX file.")

        units = self._split_markdown_into_units(markdown)

        return DocumentConversionResult(
            full_markdown=markdown,
            units=units,
            source_type="docx",
            extraction_engine="docling",
        )

    def _split_markdown_into_units(self, markdown: str) -> list[DocumentUnit]:
        blocks = [block.strip() for block in markdown.split("\n\n") if block.strip()]

        units: list[DocumentUnit] = []

        for index, block in enumerate(blocks, start=1):
            units.append(
                DocumentUnit(
                    content=block,
                    paragraph_index=index,
                )
            )

        return units
