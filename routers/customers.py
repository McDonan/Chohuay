from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.customers import CustomerCreate, CustomerUpdate
from typing import Optional

from core.database import get_db
from core.dependencies import get_current_user, require_owner
from models.customer import Customer

router = APIRouter()

@router.get("/")
async def list_customers(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    q = select(Customer).where(Customer.is_active.is_(True))
    if search:
        q = q.where(Customer.name.ilike(f"%{search}%"))
    q = q.order_by(Customer.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/")
async def create_customer(
    body: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    customer = Customer(
        name=body.name,
        phone=body.phone,
        note=body.note,
        credit_limit=body.credit_limit,
    )
    db.add(customer)
    await db.commit()
    return {"id": customer.id, "message": "เพิ่มลูกค้าเรียบร้อย"}


@router.patch("/{customer_id}")
async def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="ไม่พบลูกค้า")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(customer, field, value)
    await db.commit()
    return {"message": "อัพเดทเรียบร้อย"}