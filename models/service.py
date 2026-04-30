from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ServiceTransaction(Base):
    __tablename__ = "service_transactions"

    id         : Mapped[int]           = mapped_column(primary_key=True)
    type       : Mapped[str]           = mapped_column(String(20))   # transfer | topup
    amount     : Mapped[Decimal]       = mapped_column(Numeric(10, 2))  # เงินที่ลูกค้าโอน/เติม
    fee        : Mapped[Decimal]       = mapped_column(Numeric(10, 2))  # ค่าธรรมเนียมที่ร้านได้
    note       : Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by : Mapped[int]           = mapped_column(ForeignKey("users.id"))
    created_at : Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=func.now())
