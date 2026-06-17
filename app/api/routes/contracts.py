from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database.models import Contract
from app.database.repositories.contract_repository import ContractRepository
from app.dependencies import get_db
from app.services.ingestion_service import IngestionService

router = APIRouter()


def serialize_contract(contract: Contract) -> dict:
    return {
        "id": contract.id,
        "original_filename": contract.original_filename,
        "file_type": contract.file_type,
        "status": contract.status,
        "failed_step": contract.failed_step,
        "error_message": contract.error_message,
        "title": contract.title,
        "contract_type": contract.contract_type,
        "landlord": contract.landlord,
        "tenant": contract.tenant,
        "property_address": contract.property_address,
        "start_date": str(contract.start_date) if contract.start_date else None,
        "end_date": str(contract.end_date) if contract.end_date else None,
        "monthly_rent": contract.monthly_rent,
        "currency": contract.currency,
        "security_deposit": contract.security_deposit,
        "renewal_notice_days": contract.renewal_notice_days,
        "early_termination_notice_days": contract.early_termination_notice_days,
        "risk_level": contract.risk_level,
        "created_at": str(contract.created_at) if contract.created_at else None,
    }


@router.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ingestion_service = IngestionService(db)

    try:
        contract = await ingestion_service.ingest(file)

        if contract is None:
            raise HTTPException(status_code=500, detail="Contract was not created.")

        return {
            "message": "Contract uploaded, processed and indexed successfully.",
            "contract": serialize_contract(contract),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def list_contracts(db: Session = Depends(get_db)):
    repository = ContractRepository(db)
    contracts = repository.list_contracts()

    return {"contracts": [serialize_contract(contract) for contract in contracts]}


@router.get("/reports/expiring")
def get_expiring_contracts(
    days: int = 90,
    db: Session = Depends(get_db),
):
    repository = ContractRepository(db)
    contracts = repository.get_expiring_contracts(days=days)

    return {
        "days": days,
        "contracts": [serialize_contract(contract) for contract in contracts],
    }


@router.get("/{contract_id}")
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
):
    repository = ContractRepository(db)
    contract = repository.get_by_id(contract_id)

    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found.")

    return serialize_contract(contract)
