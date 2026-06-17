from fastapi import APIRouter
from app.schemas.request_schema import ChatRequest
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/global")
def chat_global(request: ChatRequest):
    service = RagService()

    return service.answer(
        question=request.question,
        contract_id=None,
        k=request.k,
    )


@router.post("/contract/{contract_id}")
def chat_with_contract(
    contract_id: int,
    request: ChatRequest,
):
    service = RagService()

    return service.answer(
        question=request.question,
        contract_id=contract_id,
        k=request.k,
    )
