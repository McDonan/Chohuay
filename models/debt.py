from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime
from decimal import Decimal
from typing import Optional


class DebtTransaction(Base):
    __tablename__ = "debt_transactions"

    id          : Mapped[int]           = mapped_column(primary_key=True)
    customer_id : Mapped[int]           = mapped_column(ForeignKey("customers.id"))
    type        : Mapped[str]           = mapped_column(String(10))   # charge | payment
    amount      : Mapped[Decimal]       = mapped_column(Numeric(10, 2))
    sale_id     : Mapped[Optional[int]] = mapped_column(ForeignKey("sales.id"), nullable=True)
    note        : Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by  : Mapped[int]           = mapped_column(ForeignKey("users.id"))
    created_at  : Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=func.now())
