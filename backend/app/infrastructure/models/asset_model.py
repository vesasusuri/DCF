from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.project_model import Base


class AssetModel(Base):
    __tablename__ = "assets"
    __table_args__ = {"schema": "approved"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("approved.projects.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    gla_sqm: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
