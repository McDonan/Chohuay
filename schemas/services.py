from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ServiceCreate(BaseModel):
    type: str           # transfer | topup
    amount: Decimal     # เงินที่ลูกค้าต้องการโอน/เติม
    fee: Decimal        # ค่าธรรมเนียมที่ร้านได้
    note: Optional[str] = None
