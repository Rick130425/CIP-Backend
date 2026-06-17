from pathlib import Path
from openai import OpenAI
from app.config import settings
from app.schemas.extraction_schema import ContractMetadata


class MetadataExtractionService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.prompt_template = Path(
            "app/prompts/metadata_extraction_prompt.txt"
        ).read_text(encoding="utf-8")

    def extract(self, contract_markdown: str) -> ContractMetadata:
        text_for_extraction = self._limit_text(contract_markdown)

        prompt = self.prompt_template.format(
            contract_text=text_for_extraction,
        )

        response = self.client.responses.parse(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": "You extract structured metadata from contracts.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            text_format=ContractMetadata,
        )

        return response.output_parsed

    def _limit_text(self, text: str, max_chars: int = 50_000) -> str:
        return text[:max_chars]
