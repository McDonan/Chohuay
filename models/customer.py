from sqlalchemy import Boolean, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime
from decimal import Decimal
from typing import Optional


class Customer(Base):
    __tablename__ = "customers"

    id           : Mapped[int]             = mapped_column(primary_key=True)
    name         : Mapped[str]             = mapped_column(String(200))
    phone        : Mapped[Optional[str]]   = mapped_column(String(20), nullable=True)
    note         : Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    credit_limit : Mapped[Decimal]         = mapped_column(Numeric(10, 2), default=500)
    is_active    : Mapped[bool]            = mapped_column(Boolean, default=True)
    created_at   : Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=func.now())
