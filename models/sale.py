import enum
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime
from decimal import Decimal
from typing import Optional

class PaymentMethod(enum.Enum):
    CASH = 'cash'
    QR = 'qr'

class Sale(Base):
    __tablename__ = "sales"

    id             : Mapped[int]             = mapped_column(primary_key=True)
    customer_id    : Mapped[Optional[int]]   = mapped_column(ForeignKey("customers.id"), nullable=True)
    is_credit      : Mapped[bool]            = mapped_column(Boolean, default=False)
    payment_method : Mapped[PaymentMethod]   = mapped_column(
        Enum(PaymentMethod, native_enum=False, name="sale_payment_method"),
        default=PaymentMethod.CASH
    )
    slip_image_url : Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    total_amount   : Mapped[Decimal]         = mapped_column(Numeric(10, 2))
    total_cost     : Mapped[Decimal]         = mapped_column(Numeric(10, 2))
    note           : Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    created_by     : Mapped[int]             = mapped_column(ForeignKey("users.id"))
    created_at     : Mapped[datetime]        = mapped_column(DateTime(timezone=True), default=func.now())
    cancelled_at   : Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by   : Mapped[Optional[int]]   = mapped_column(ForeignKey("users.id"), nullable=True)


class SaleItem(Base):
    __tablename__ = "sale_items"

    id             : Mapped[int]             = mapped_column(primary_key=True)
    sale_id        : Mapped[int]             = mapped_column(ForeignKey("sales.id"))
    product_id     : Mapped[int]             = mapped_column(ForeignKey("products.id"))
    variant_id     : Mapped[Optional[int]]   = mapped_column(ForeignKey("product_variants.id"), nullable=True)
    qty            : Mapped[Decimal]         = mapped_column(Numeric(10, 3))
    unit_price     : Mapped[Decimal]         = mapped_column(Numeric(10, 2))
    unit_cost      : Mapped[Decimal]         = mapped_column(Numeric(10, 2))
    bundle_rule_id : Mapped[Optional[int]]   = mapped_column(ForeignKey("bundle_rules.id"), nullable=True)