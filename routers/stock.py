from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.stock import RestockRequest

from core.database import get_db
from core.dependencies import require_owner
from models.stock import Stock, PurchaseLog
from models.product import Product

router = APIRouter()

@router.post("/restock")
async def restock(
    body: RestockRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    """รับสินค้าเข้าสต๊อก + บันทึก purchase log"""
    product = await db.get(Product, body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

    # อัพเดทสต๊อก
    result = await db.execute(
        select(Stock).where(Stock.product_id == body.product_id)
    )
    stock = result.scalar_one_or_none()
    if stock:
        stock.quantity += body.qty
    else:
        db.add(Stock(product_id=body.product_id, quantity=body.qty))

    # บันทึก log ทุกครั้ง (เก็บประวัติต้นทุนแต่ละรอบ)
    db.add(PurchaseLog(
        product_id=body.product_id,
        variant_id=body.variant_id,
        qty=body.qty,
        unit_cost=body.unit_cost,
        total_cost=body.qty * body.unit_cost,
        source=body.source,
        note=body.note,
        created_by=user["id"],
    ))

    # อัพเดท cost_price ของสินค้าเป็นราคาล่าสุด
    product.cost_price = body.unit_cost

    await db.commit()
    return {"message": "รับสินค้าเข้าเรียบร้อย", "new_qty": float(stock.quantity if stock else body.qty)}


@router.get("/")
async def list_stock(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    result = await db.execute(
        select(Product, Stock)
        .join(Stock, Stock.product_id == Product.id, isouter=True)
        .where(Product.is_active.is_(True))
        .order_by(Product.name)
    )
    rows = result.all()
    return [
        {
            "product_id": p.id,
            "name": p.name,
            "sell_unit": p.sell_unit,
            "quantity": float(s.quantity) if s else 0,
            "min_qty": float(s.min_qty) if s else 5,
            "is_low": (s.quantity <= s.min_qty) if s else True,
        }
        for p, s in rows
    ]


@router.get("/purchase-history/{product_id}")
async def purchase_history(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    """ดูประวัติราคาทุนย้อนหลัง ช่วยวิเคราะห์ว่าซื้อจากไหนถูกกว่า"""
    result = await db.execute(
        select(PurchaseLog)
        .where(PurchaseLog.product_id == product_id)
        .order_by(PurchaseLog.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()