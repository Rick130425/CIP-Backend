from sqlalchemy.orm import Session
from langchain_core.documents import Document
from app.database.models import ContractChunk


class ChunkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_chunks(
        self,
        *,
        contract_id: int,
        chunks: list[Document],
    ) -> list[ContractChunk]:
        saved_chunks: list[ContractChunk] = []

        for chunk in chunks:
            metadata = chunk.metadata
            chunk_index = metadata["chunk_index"]

            chroma_id = f"contract-{contract_id}-chunk-{chunk_index}"

            db_chunk = ContractChunk(
                contract_id=contract_id,
                chunk_index=chunk_index,
                content=chunk.page_content,
                source_file=metadata.get("source_file", ""),
                page_number=metadata.get("page_number"),
                paragraph_index=metadata.get("paragraph_index"),
                line_start=metadata.get("line_start"),
                line_end=metadata.get("line_end"),
                section_title=metadata.get("section_title"),
                chroma_id=chroma_id,
            )

            self.db.add(db_chunk)
            saved_chunks.append(db_chunk)

        self.db.commit()

        return saved_chunks
