from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.database.models import Contract, ContractStatus
from app.schemas.extraction_schema import ContractMetadata


class ContractRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_hash(self, file_hash: str) -> Contract | None:
        return self.db.query(Contract).filter(Contract.file_hash == file_hash).first()

    def get_by_id(self, contract_id: int) -> Contract | None:
        return self.db.get(Contract, contract_id)

    def list_contracts(self) -> list[Contract]:
        return self.db.query(Contract).order_by(Contract.created_at.desc()).all()

    def create_uploaded(
        self,
        *,
        original_filename: str,
        stored_filename: str,
        stored_file_path: str,
        file_type: str,
        file_hash: str,
    ) -> Contract:
        contract = Contract(
            original_filename=original_filename,
            stored_filename=stored_filename,
            stored_file_path=stored_file_path,
            file_type=file_type,
            file_hash=file_hash,
            status=ContractStatus.UPLOADED.value,
        )

        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)

        return contract

    def save_extracted_markdown(self, contract_id: int, markdown: str) -> None:
        contract = self.db.get(Contract, contract_id)

        if contract is None:
            raise ValueError(f"Contract {contract_id} not found.")

        contract.extracted_markdown = markdown
        contract.status = ContractStatus.TEXT_EXTRACTED.value

        self.db.commit()

    def save_metadata(self, contract_id: int, metadata: ContractMetadata) -> None:
        contract = self.db.get(Contract, contract_id)

        if contract is None:
            raise ValueError(f"Contract {contract_id} not found.")

        contract.title = metadata.title
        contract.contract_type = metadata.contract_type
        contract.landlord = metadata.landlord
        contract.tenant = metadata.tenant
        contract.property_address = metadata.property_address

        contract.start_date = self._parse_date(metadata.start_date)
        contract.end_date = self._parse_date(metadata.end_date)

        contract.monthly_rent = metadata.monthly_rent
        contract.currency = metadata.currency
        contract.security_deposit = metadata.security_deposit

        contract.renewal_notice_days = metadata.renewal_notice_days
        contract.early_termination_notice_days = metadata.early_termination_notice_days

        contract.risk_level = metadata.risk_level
        contract.status = ContractStatus.METADATA_EXTRACTED.value

        self.db.commit()

    def mark_indexed(self, contract_id: int) -> None:
        contract = self.db.get(Contract, contract_id)

        if contract is None:
            raise ValueError(f"Contract {contract_id} not found.")

        contract.status = ContractStatus.INDEXED.value
        contract.failed_step = None
        contract.error_message = None

        self.db.commit()

    def mark_failed(
        self,
        contract_id: int,
        *,
        failed_step: str,
        error_message: str,
    ) -> None:
        contract = self.db.get(Contract, contract_id)

        if contract is None:
            return

        contract.status = ContractStatus.FAILED.value
        contract.failed_step = failed_step
        contract.error_message = error_message

        self.db.commit()

    def get_expiring_contracts(self, days: int = 90) -> list[Contract]:
        today = datetime.utcnow().date()
        limit_date = today + timedelta(days=days)

        return (
            self.db.query(Contract)
            .filter(Contract.end_date.isnot(None))
            .filter(Contract.end_date >= today)
            .filter(Contract.end_date <= limit_date)
            .order_by(Contract.end_date.asc())
            .all()
        )

    def _parse_date(self, value: str | None) -> date | None:
        if value is None:
            return None

        return date.fromisoformat(value)
