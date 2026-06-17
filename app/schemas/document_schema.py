from typing import Literal
from pydantic import BaseModel


class DocumentUnit(BaseModel):
    content: str

    page_number: int | None = None
    paragraph_index: int | None = None
    line_start: int | None = None
    line_end: int | None = None

    section_title: str | None = None


class DocumentConversionResult(BaseModel):
    full_markdown: str
    units: list[DocumentUnit]

    source_type: Literal["pdf", "docx", "txt"]
    extraction_engine: str
