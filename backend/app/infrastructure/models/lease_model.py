from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.project_model import Base


class LeaseModel(Base):
    __tablename__ = "leases"
    __table_args__ = {"schema": "approved"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    unit_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    tenant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    passing_rent: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    indexation_type: Mapped[str] = mapped_column(String(50), nullable=False, server_default="none")
    indexation_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)
    break_option_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    has_extension_option: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
