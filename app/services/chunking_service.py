from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingService:
    def __init__(self) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=150,
            separators=[
                "\n\n",
                "\n",
                ". ",
                "; ",
                ", ",
                " ",
                "",
            ],
        )

    def split(self, documents: list[Document]) -> list[Document]:
        chunks = self.splitter.split_documents(documents)

        clean_chunks: list[Document] = []

        for index, chunk in enumerate(chunks):
            content = chunk.page_content.strip()

            if not content:
                continue

            chunk.metadata["chunk_index"] = index
            chunk.page_content = content

            clean_chunks.append(chunk)

        return clean_chunks
