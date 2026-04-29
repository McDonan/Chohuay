from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class RestockRequest(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    qty: Decimal
    unit_cost: Decimal
    source: str = "other"
    note: Optional[str] = None
