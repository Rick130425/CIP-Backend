from fastapi import APIRouter
from app.schemas.request_schema import SemanticSearchRequest
from app.services.vector_store_service import VectorStoreService

router = APIRouter()


@router.post("/semantic")
def semantic_search(request: SemanticSearchRequest):
    service = VectorStoreService()

    results = service.semantic_search(
        query=request.query,
        contract_id=request.contract_id,
        k=request.k,
    )

    return {
        "query": request.query,
        "results": results,
    }
