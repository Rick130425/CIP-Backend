from pathlib import Path
from openai import OpenAI
from app.config import settings
from app.services.vector_store_service import VectorStoreService


class RagService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.vector_store_service = VectorStoreService()
        self.prompt_template = Path("app/prompts/rag_answer_prompt.txt").read_text(
            encoding="utf-8"
        )

    def answer(
        self,
        *,
        question: str,
        contract_id: int | None = None,
        k: int = 5,
    ) -> dict:
        search_results = self.vector_store_service.semantic_search(
            query=question,
            contract_id=contract_id,
            k=k,
        )

        context = self._build_context(search_results)

        prompt = self.prompt_template.format(
            context=context,
            question=question,
        )

        response = self.client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": "You answer questions about contracts using retrieved context.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return {
            "answer": response.output_text,
            "sources": [
                {
                    "source_file": result["metadata"].get("source_file"),
                    "page_number": result["metadata"].get("page_number"),
                    "paragraph_index": result["metadata"].get("paragraph_index"),
                    "line_start": result["metadata"].get("line_start"),
                    "line_end": result["metadata"].get("line_end"),
                    "section_title": result["metadata"].get("section_title"),
                    "contract_id": result["metadata"].get("contract_id"),
                    "score": result["score"],
                }
                for result in search_results
            ],
        }

    def _build_context(self, search_results: list[dict]) -> str:
        context_parts: list[str] = []

        for index, result in enumerate(search_results, start=1):
            metadata = result["metadata"]
            content = result["content"]

            source = metadata.get("source_file", "unknown source")

            location_parts = []

            if metadata.get("page_number") is not None:
                location_parts.append(f"page {metadata['page_number']}")

            if metadata.get("paragraph_index") is not None:
                location_parts.append(f"paragraph {metadata['paragraph_index']}")

            if (
                metadata.get("line_start") is not None
                and metadata.get("line_end") is not None
            ):
                location_parts.append(
                    f"lines {metadata['line_start']}-{metadata['line_end']}"
                )

            location = ", ".join(location_parts)

            context_parts.append(f"[Source {index}: {source} {location}]\n{content}")

        return "\n\n---\n\n".join(context_parts)
