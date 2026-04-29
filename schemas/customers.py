from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    note: Optional[str] = None
    credit_limit: Decimal = Decimal("500")

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    note: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    is_active: Optional[bool] = None
