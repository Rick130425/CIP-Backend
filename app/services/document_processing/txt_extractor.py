from pathlib import Path

from app.schemas.document_schema import DocumentConversionResult, DocumentUnit
from app.services.document_processing.base import BaseDocumentExtractor
from app.services.markdown_normalization_service import MarkdownNormalizationService


class TxtExtractor(BaseDocumentExtractor):
    def __init__(self) -> None:
        self.normalizer = MarkdownNormalizationService()

    def extract(self, file_path: str) -> DocumentConversionResult:
        raw_text = Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore",
        )

        markdown = self.normalizer.normalize(raw_text)

        if len(markdown) < 100:
            raise ValueError("No extractable text found in TXT file.")

        units = self._split_lines_into_units(markdown)

        return DocumentConversionResult(
            full_markdown=markdown,
            units=units,
            source_type="txt",
            extraction_engine="python-native",
        )

    def _split_lines_into_units(
        self,
        text: str,
        lines_per_unit: int = 30,
    ) -> list[DocumentUnit]:
        lines = text.splitlines()
        units: list[DocumentUnit] = []

        for start in range(0, len(lines), lines_per_unit):
            end = min(start + lines_per_unit, len(lines))
            block = "\n".join(lines[start:end]).strip()

            if not block:
                continue

            units.append(
                DocumentUnit(
                    content=block,
                    line_start=start + 1,
                    line_end=end,
                )
            )

        return units
