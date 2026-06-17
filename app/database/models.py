from datetime import date, datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class ContractStatus(str, Enum):
    UPLOADED = "uploaded"
    TEXT_EXTRACTED = "text_extracted"
    METADATA_EXTRACTED = "metadata_extracted"
    INDEXED = "indexed"
    FAILED = "failed"


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_hash: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default=ContractStatus.UPLOADED.value,
        nullable=False,
    )

    failed_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    extracted_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contract_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    landlord: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tenant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    property_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    monthly_rent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    security_deposit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    renewal_notice_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    early_termination_notice_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True,
    )

    chunks: Mapped[list["ContractChunk"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )


class ContractChunk(Base):
    __tablename__ = "contract_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    source_file: Mapped[str] = mapped_column(String(255), nullable=False)

    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    paragraph_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    section_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    chroma_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    contract: Mapped["Contract"] = relationship(back_populates="chunks")
