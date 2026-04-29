from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class SaleItemIn(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    qty: Decimal
    unit_price: Decimal
    unit_cost: Decimal
    bundle_rule_id: Optional[int] = None

class CreateSaleRequest(BaseModel):
    customer_id: Optional[int] = None
    is_credit: bool = False
    payment_method: str = "cash"
    items: list[SaleItemIn]
    note: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    total_amount: Decimal
    total_cost: Decimal
    profit: Decimal
