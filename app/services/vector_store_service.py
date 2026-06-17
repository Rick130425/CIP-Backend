from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from app.config import settings


class VectorStoreService:
    def __init__(self) -> None:
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )

        self.vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir,
        )

    def index_chunks(
        self,
        *,
        contract_id: int,
        chunks: list[Document],
    ) -> None:
        documents: list[Document] = []
        ids: list[str] = []

        for chunk in chunks:
            chunk_index = chunk.metadata["chunk_index"]
            chroma_id = f"contract-{contract_id}-chunk-{chunk_index}"

            chunk.metadata["chroma_id"] = chroma_id

            documents.append(chunk)
            ids.append(chroma_id)

        self.vector_store.add_documents(
            documents=documents,
            ids=ids,
        )

    def semantic_search(
        self,
        *,
        query: str,
        contract_id: int | None = None,
        k: int = 5,
    ) -> list[dict]:
        where_filter = None

        if contract_id is not None:
            where_filter = {"contract_id": contract_id}

        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=where_filter,
        )

        formatted_results: list[dict] = []

        for document, score in results:
            formatted_results.append(
                {
                    "content": document.page_content,
                    "metadata": document.metadata,
                    "score": score,
                }
            )

        return formatted_results

    def delete_contract_vectors(self, contract_id: int) -> None:
        existing = self.vector_store.get(where={"contract_id": contract_id})

        ids = existing.get("ids", [])

        if ids:
            self.vector_store.delete(ids=ids)
