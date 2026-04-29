from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class PayDebtRequest(BaseModel):
    customer_id: int
    amount: Decimal
    note: Optional[str] = None
