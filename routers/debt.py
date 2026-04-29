from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from schemas.debt import PayDebtRequest
from decimal import Decimal

from core.database import get_db
from core.dependencies import require_owner
from models.debt import DebtTransaction
from models.customer import Customer

router = APIRouter()

@router.post("/payment")
async def pay_debt(
    body: PayDebtRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),   # เฉพาะ owner รับเงิน
):
    customer = await db.get(Customer, body.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="ไม่พบลูกค้า")

    # เช็คว่ายอดหนี้มีพอให้จ่ายมั้ย
    balance_row = await db.execute(
        text("SELECT balance FROM customer_balance WHERE customer_id = :id"),
        {"id": body.customer_id}
    )
    balance = balance_row.scalar() or Decimal("0")

    if body.amount > balance:
        raise HTTPException(
            status_code=400,
            detail=f"จ่ายเกินยอดหนี้ (ยอดคงค้าง ฿{balance})"
        )

    db.add(DebtTransaction(
        customer_id = body.customer_id,
        type        = "payment",
        amount      = body.amount,
        note        = body.note,
        created_by  = user["id"],
    ))
    await db.commit()
    return {"message": "บันทึกการชำระเงินเรียบร้อย", "remaining": balance - body.amount}

@router.get("/customer/{customer_id}")
async def get_customer_debt(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    """ดูประวัติหนี้ทั้งหมดของลูกค้า พร้อม running balance"""
    txs = await db.execute(
        select(DebtTransaction)
        .where(DebtTransaction.customer_id == customer_id)
        .order_by(DebtTransaction.created_at)
    )
    rows = txs.scalars().all()

    running = Decimal("0")
    history = []
    for tx in rows:
        if tx.type == "charge":
            running += tx.amount
        else:
            running -= tx.amount
        history.append({
            "id"        : tx.id,
            "type"      : tx.type,
            "amount"    : tx.amount,
            "balance"   : running,
            "note"      : tx.note,
            "created_at": tx.created_at,
        })

    return {"customer_id": customer_id, "current_balance": running, "history": history}

@router.get("/overview")
async def debt_overview(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    """สรุปหนี้ทุกคน เรียงตามยอดมาก→น้อย"""
    result = await db.execute(
        text("""
            SELECT customer_id, name, balance, credit_limit, last_transaction
            FROM customer_balance
            WHERE balance > 0
            ORDER BY balance DESC
        """)
    )
    return result.mappings().all()