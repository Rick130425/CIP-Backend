from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    contract_id: int | None = None
    k: int = 5


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    k: int = 5
