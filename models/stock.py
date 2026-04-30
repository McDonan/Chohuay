import enum
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime
from decimal import Decimal
from typing import Optional

class CostSource(enum.Enum):
    MAKRO = 'makro'
    SUPER_CHEAP = 'super_cheap'
    MARKET = 'market'
    DELIVERY = 'delivery'
    FARM = 'farm'
    OTHER = 'other'

class Stock(Base):
    __tablename__ = "stock"

    id         : Mapped[int]     = mapped_column(primary_key=True)
    product_id : Mapped[int]     = mapped_column(ForeignKey("products.id"), unique=True)
    variant_id : Mapped[Optional[int]] = mapped_column(ForeignKey("product_variants.id"), nullable=True)
    quantity   : Mapped[Decimal] = mapped_column(Numeric(10, 3), default=0)
    min_qty    : Mapped[Decimal] = mapped_column(Numeric(10, 3), default=5)
    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
    )


class PurchaseLog(Base):
    __tablename__ = "purchase_logs"

    id         : Mapped[int]             = mapped_column(primary_key=True)
    product_id : Mapped[int]             = mapped_column(ForeignKey("products.id"))
    variant_id : Mapped[Optional[int]]   = mapped_column(ForeignKey("product_variants.id"), nullable=True)
    qty        : Mapped[Decimal]         = mapped_column(Numeric(10, 3))
    unit_cost  : Mapped[Decimal]         = mapped_column(Numeric(10, 2))
    total_cost : Mapped[Decimal]         = mapped_column(Numeric(10, 2))
    source     : Mapped[CostSource]      = mapped_column(Enum(CostSource, name="cost_source", create_type=True), default=CostSource.OTHER)
    note       : Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    created_by : Mapped[int]             = mapped_column(ForeignKey("users.id"))
    created_at : Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=func.now())
