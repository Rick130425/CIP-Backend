from typing import Literal
from pydantic import BaseModel, Field


class ContractMetadata(BaseModel):
    title: str | None = Field(default=None)
    contract_type: str | None = Field(default=None)

    landlord: str | None = Field(default=None)
    tenant: str | None = Field(default=None)
    property_address: str | None = Field(default=None)

    start_date: str | None = Field(
        default=None,
        description="Contract start date in YYYY-MM-DD format.",
    )

    end_date: str | None = Field(
        default=None,
        description="Contract end date in YYYY-MM-DD format.",
    )

    monthly_rent: float | None = Field(default=None)
    currency: Literal["MXN", "USD", "EUR"] | None = Field(default=None)
    security_deposit: float | None = Field(default=None)

    renewal_notice_days: int | None = Field(default=None)
    early_termination_notice_days: int | None = Field(default=None)

    risk_level: Literal["low", "medium", "high", "unknown"] = "unknown"
