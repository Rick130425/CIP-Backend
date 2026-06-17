from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.database.repositories.chunk_repository import ChunkRepository
from app.database.repositories.contract_repository import ContractRepository
from app.services.chunking_service import ChunkingService
from app.services.document_processing.document_extraction_service import (
    DocumentExtractionService,
)
from app.services.file_storage_service import FileStorageService
from app.services.file_validation_service import FileValidationService
from app.services.langchain_document_service import LangChainDocumentService
from app.services.metadata_extraction_service import MetadataExtractionService
from app.services.vector_store_service import VectorStoreService
from app.utils.hash_utils import calculate_sha256


class IngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db

        self.file_validator = FileValidationService()
        self.file_storage = FileStorageService()
        self.document_extractor = DocumentExtractionService()
        self.metadata_extractor = MetadataExtractionService()
        self.langchain_document_service = LangChainDocumentService()
        self.chunking_service = ChunkingService()
        self.vector_store_service = VectorStoreService()

        self.contract_repository = ContractRepository(db)
        self.chunk_repository = ChunkRepository(db)

    async def ingest(self, file: UploadFile):
        content = await self.file_validator.validate(file)

        file_hash = calculate_sha256(content)

        existing_contract = self.contract_repository.get_by_hash(file_hash)

        if existing_contract:
            return existing_contract

        stored_filename, stored_file_path = self.file_storage.save(
            original_filename=file.filename or "uploaded_contract",
            content=content,
        )

        file_type = (
            Path(file.filename or stored_filename).suffix.lower().replace(".", "")
        )

        contract = self.contract_repository.create_uploaded(
            original_filename=file.filename or stored_filename,
            stored_filename=stored_filename,
            stored_file_path=stored_file_path,
            file_type=file_type,
            file_hash=file_hash,
        )

        try:
            try:
                conversion_result = self.document_extractor.extract(stored_file_path)
            except Exception as e:
                self.contract_repository.mark_failed(
                    contract.id,
                    failed_step="document_extraction",
                    error_message=str(e),
                )
                raise

            try:
                self.contract_repository.save_extracted_markdown(
                    contract_id=contract.id,
                    markdown=conversion_result.full_markdown,
                )
            except Exception as e:
                self.contract_repository.mark_failed(
                    contract.id,
                    failed_step="markdown_persistence",
                    error_message=str(e),
                )
                raise

            try:
                metadata = self.metadata_extractor.extract(
                    conversion_result.full_markdown
                )
            except Exception as e:
                self.contract_repository.mark_failed(
                    contract.id,
                    failed_step="metadata_extraction",
                    error_message=str(e),
                )
                raise

            try:
                self.contract_repository.save_metadata(
                    contract_id=contract.id,
                    metadata=metadata,
                )
            except Exception as e:
                self.contract_repository.mark_failed(
                    contract.id,
                    failed_step="metadata_persistence",
                    error_message=str(e),
                )
                raise

            try:
                refreshed_contract = self.contract_repository.get_by_id(contract.id)

                if refreshed_contract is None:
                    raise ValueError(f"Contract {contract.id} not found.")

                documents = self.langchain_document_service.build_documents(
                    contract=refreshed_contract,
                    conversion_result=conversion_result,
                )

                chunks = self.chunking_service.split(documents)

                if not chunks:
                    raise ValueError("No chunks were generated from the contract.")

            except Exception as e:
                self.contract_repository.mark_failed(
                    contract.id,
                    failed_step="chunking",
                    error_message=str(e),
                )
                raise

            try:
                self.chunk_repository.save_chunks(
                    contract_id=contract.id,
                    chunks=chunks,
                )
            except Exception as e:
                self.contract_repository.mark_failed(
                    contract.id,
                    failed_step="chunk_persistence",
                    error_message=str(e),
                )
                raise

            try:
                self.vector_store_service.index_chunks(
                    contract_id=contract.id,
                    chunks=chunks,
                )
            except Exception as e:
                self.contract_repository.mark_failed(
                    contract.id,
                    failed_step="vector_indexing",
                    error_message=str(e),
                )
                raise

            self.contract_repository.mark_indexed(contract.id)

            return self.contract_repository.get_by_id(contract.id)

        except Exception:
            raise
