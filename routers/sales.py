from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from schemas.sales import CreateSaleRequest, SaleResponse

from core.database import get_db
from core.dependencies import get_current_user
from models.sale import Sale, SaleItem
from models.stock import Stock
from models.product import Product
from models.debt import DebtTransaction
from models.product import BundleRule

router = APIRouter()

# ── Endpoints ────────────────────────────────────────────────

@router.post("/", response_model=SaleResponse)
async def create_sale(
    body: CreateSaleRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # staff ขายได้ แต่ credit ต้องเป็น owner เท่านั้น
    if body.is_credit and user["role"] != "owner":
        raise HTTPException(status_code=403, detail="การติดหนี้ต้องให้เจ้าของอนุมัติ")

    total_amount = sum(i.unit_price * i.qty for i in body.items)
    total_cost   = sum(i.unit_cost  * i.qty for i in body.items)

    sale = Sale(
        customer_id    = body.customer_id,
        is_credit      = body.is_credit,
        payment_method = body.payment_method,
        total_amount   = total_amount,
        total_cost     = total_cost,
        note           = body.note,
        created_by     = user["id"],
    )
    db.add(sale)
    await db.flush()  # ได้ sale.id

    for item in body.items:
        db.add(SaleItem(
            sale_id        = sale.id,
            product_id     = item.product_id,
            variant_id     = item.variant_id,
            qty            = item.qty,
            unit_price     = item.unit_price,
            unit_cost      = item.unit_cost,
            bundle_rule_id = item.bundle_rule_id,
        ))

        # ตัดสต๊อก (lock row ป้องกัน race condition)
        result = await db.execute(
            update(Stock)
            .where(Stock.product_id == item.product_id, Stock.quantity >= item.qty)
            .values(quantity=Stock.quantity - item.qty)
            .returning(Stock.quantity)
        )
        if not result.fetchone():
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"สินค้า id={item.product_id} สต๊อกไม่พอ")

    # ถ้าติดหนี้ → บันทึก debt transaction
    if body.is_credit and body.customer_id:
        db.add(DebtTransaction(
            customer_id = body.customer_id,
            type        = "charge",
            amount      = total_amount,
            sale_id     = sale.id,
            created_by  = user["id"],
        ))

    await db.commit()

    return SaleResponse(
        id           = sale.id,
        total_amount = total_amount,
        total_cost   = total_cost,
        profit       = total_amount - total_cost,
    )

@router.delete("/{sale_id}")
async def cancel_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Soft cancel — คืนสต๊อก, ยกเลิกหนี้ที่ผูกอยู่"""
    if user["role"] != "owner":
        raise HTTPException(status_code=403, detail="เฉพาะเจ้าของร้านเท่านั้น")

    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    sale = result.scalar_one_or_none()

    if not sale:
        raise HTTPException(status_code=404, detail="ไม่พบบิลนี้")
    if sale.cancelled_at:
        raise HTTPException(status_code=400, detail="ยกเลิกบิลนี้ไปแล้ว")

    sale.cancelled_at = datetime.now(timezone.utc)
    sale.cancelled_by = user["id"]

    # คืนสต๊อก
    items = await db.execute(select(SaleItem).where(SaleItem.sale_id == sale_id))
    for item in items.scalars():
        await db.execute(
            update(Stock)
            .where(Stock.product_id == item.product_id)
            .values(quantity=Stock.quantity + item.qty)
        )

    await db.commit()
    return {"message": "ยกเลิกบิลเรียบร้อย"}

@router.get("/bundle-price/{product_id}")
async def get_bundle_price(
    product_id: int,
    qty: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    prod = await db.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

    # Fetch bundle rule for this product
    result = await db.execute(
        select(BundleRule).where(BundleRule.product_id == product_id)
    )
    rule = result.scalar_one_or_none()

    if rule:
        sets = qty // rule.min_qty
        remainder = qty % rule.min_qty
        total = (sets * rule.bundle_price) + (remainder * prod.sell_price)
        return {
            "has_bundle"    : True,
            "bundle_rule_id": rule.id,
            "sets"          : sets,
            "remainder"     : remainder,
            "total_price"   : float(total),
            "unit_price"    : round(float(total) / qty, 2) if qty else 0,
        }
    else:
        total = prod.sell_price * qty
        return {
            "has_bundle"    : False,
            "bundle_rule_id": None,
            "sets"          : 0,
            "remainder"     : qty,
            "total_price"   : float(total),
            "unit_price"    : round(float(total) / qty, 2) if qty else 0,
        }