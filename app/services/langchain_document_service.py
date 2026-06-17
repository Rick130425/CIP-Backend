from langchain_core.documents import Document
from app.database.models import Contract
from app.schemas.document_schema import DocumentConversionResult


class LangChainDocumentService:
    def build_documents(
        self,
        *,
        contract: Contract,
        conversion_result: DocumentConversionResult,
    ) -> list[Document]:
        documents: list[Document] = []

        for unit_index, unit in enumerate(conversion_result.units):
            metadata = {
                "contract_id": contract.id,
                "source_file": contract.original_filename,
                "stored_file_path": contract.stored_file_path,
                "file_type": contract.file_type,
                "source_type": conversion_result.source_type,
                "extraction_engine": conversion_result.extraction_engine,
                "unit_index": unit_index,
                "contract_type": contract.contract_type or "",
                "tenant": contract.tenant or "",
                "landlord": contract.landlord or "",
                "end_date": str(contract.end_date) if contract.end_date else "",
            }

            if unit.page_number is not None:
                metadata["page_number"] = unit.page_number

            if unit.paragraph_index is not None:
                metadata["paragraph_index"] = unit.paragraph_index

            if unit.line_start is not None:
                metadata["line_start"] = unit.line_start

            if unit.line_end is not None:
                metadata["line_end"] = unit.line_end

            if unit.section_title is not None:
                metadata["section_title"] = unit.section_title

            documents.append(
                Document(
                    page_content=unit.content,
                    metadata=metadata,
                )
            )

        return documents
