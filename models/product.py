from sqlalchemy import String, Boolean, Numeric, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

class Category(Base):
    __tablename__ = "categories"
    id   : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(100))

class Product(Base):
    __tablename__ = "products"

    id                : Mapped[int]             = mapped_column(primary_key=True)
    category_id       : Mapped[Optional[int]]   = mapped_column(ForeignKey("categories.id"), nullable=True)
    name              : Mapped[str]             = mapped_column(String(200))
    product_type      : Mapped[str]             = mapped_column(String(20), default="unit")
    barcode           : Mapped[Optional[str]]   = mapped_column(String(100), nullable=True)
    cost_source       : Mapped[str]             = mapped_column(String(20), default="other")

    cost_price        : Mapped[Optional[Decimal]] = mapped_column(Numeric(10,2), nullable=True)
    sell_price        : Mapped[Decimal]           = mapped_column(Numeric(10,2))
    sell_unit         : Mapped[str]               = mapped_column(String(50), default="ชิ้น")

    bulk_unit         : Mapped[Optional[str]]     = mapped_column(String(50), nullable=True)
    bulk_qty          : Mapped[Optional[Decimal]] = mapped_column(Numeric(10,3), nullable=True)
    bulk_cost         : Mapped[Optional[Decimal]] = mapped_column(Numeric(10,2), nullable=True)
    sell_qty_per_unit : Mapped[Optional[Decimal]] = mapped_column(Numeric(10,3), nullable=True)

    is_active         : Mapped[bool]             = mapped_column(Boolean, default=True)
    deleted_at        : Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at        : Mapped[datetime]          = mapped_column(default=datetime.now(timezone.utc))

    @property
    def computed_cost(self) -> Optional[Decimal]:
        """ต้นทุนต่อหน่วยขาย สำหรับ bulk_weight"""
        if self.product_type == "bulk_weight" and self.bulk_qty and self.sell_qty_per_unit and self.bulk_cost:
            units = self.bulk_qty / self.sell_qty_per_unit
            return round(self.bulk_cost / units, 2)
        return self.cost_price

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id         : Mapped[int]             = mapped_column(primary_key=True)
    product_id : Mapped[int]             = mapped_column(ForeignKey("products.id"))
    name       : Mapped[str]             = mapped_column(String(100))
    cost_price : Mapped[Optional[Decimal]] = mapped_column(Numeric(10,2), nullable=True)
    sell_price : Mapped[Decimal]          = mapped_column(Numeric(10,2))
    is_active  : Mapped[bool]             = mapped_column(Boolean, default=True)

class BundleRule(Base):
    __tablename__ = "bundle_rules"

    id           : Mapped[int]     = mapped_column(primary_key=True)
    product_id   : Mapped[int]     = mapped_column(ForeignKey("products.id"))
    min_qty      : Mapped[int]     = mapped_column(Integer)
    bundle_price : Mapped[Decimal] = mapped_column(Numeric(10,2))
    is_active    : Mapped[bool]    = mapped_column(Boolean, default=True)