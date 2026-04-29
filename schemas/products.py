from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    product_type: str = "unit"
    barcode: Optional[str] = None
    cost_source: str = "other"
    sell_price: Decimal
    sell_unit: str = "ชิ้น"
    cost_price: Optional[Decimal] = None
    bulk_unit: Optional[str] = None
    bulk_qty: Optional[Decimal] = None
    bulk_cost: Optional[Decimal] = None
    sell_qty_per_unit: Optional[Decimal] = None
    initial_qty: Decimal = Decimal("0")
    min_qty: Decimal = Decimal("5")

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sell_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    bulk_cost: Optional[Decimal] = None
    bulk_qty: Optional[Decimal] = None
    sell_qty_per_unit: Optional[Decimal] = None
    min_qty: Optional[Decimal] = None
    is_active: Optional[bool] = None

class BundleRuleCreate(BaseModel):
    min_qty: int
    bundle_price: Decimal
