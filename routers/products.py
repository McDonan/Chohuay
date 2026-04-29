from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from schemas.products import ProductCreate, ProductUpdate, BundleRuleCreate
from decimal import Decimal
from typing import Optional
from datetime import datetime, timezone

from core.database import get_db
from core.dependencies import get_current_user, require_owner
from models.product import Product, ProductVariant, BundleRule, Category
from models.stock import Stock

router = APIRouter()

# ── Helpers ──────────────────────────────────────────────────

def product_to_dict(p: Product, stock_qty: Optional[Decimal] = None) -> dict:
    computed_cost = p.cost_price
    if p.product_type == "bulk_weight" and p.bulk_qty and p.sell_qty_per_unit and p.bulk_cost:
        units = p.bulk_qty / p.sell_qty_per_unit
        computed_cost = round(p.bulk_cost / units, 2)

    return {
        "id": p.id,
        "name": p.name,
        "product_type": p.product_type,
        "barcode": p.barcode,
        "sell_price": p.sell_price,
        "sell_unit": p.sell_unit,
        "cost_price": computed_cost,
        "cost_source": p.cost_source,
        "is_active": p.is_active,
        "stock_qty": stock_qty,
    }


# ── Endpoints ────────────────────────────────────────────────

@router.get("/")
async def list_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    q = select(Product, Stock).join(Stock, Stock.product_id == Product.id, isouter=True)
    q = q.where(Product.is_active.is_(True), Product.deleted_at.is_(None))

    if search:
        q = q.where(or_(
            Product.name.ilike(f"%{search}%"),
            Product.barcode == search,
        ))
    if category_id:
        q = q.where(Product.category_id == category_id)

    result = await db.execute(q)
    rows = result.all()
    return [product_to_dict(p, s.quantity if s else None) for p, s in rows]


@router.get("/search-barcode/{barcode}")
async def search_by_barcode(
    barcode: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(
        select(Product).where(Product.barcode == barcode, Product.is_active.is_(True), Product.deleted_at.is_(None))
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้าจาก barcode นี้")
    return product_to_dict(product)


@router.post("/")
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    product = Product(
        name=body.name,
        category_id=body.category_id,
        product_type=body.product_type,
        barcode=body.barcode,
        cost_source=body.cost_source,
        sell_price=body.sell_price,
        sell_unit=body.sell_unit,
        cost_price=body.cost_price,
        bulk_unit=body.bulk_unit,
        bulk_qty=body.bulk_qty,
        bulk_cost=body.bulk_cost,
        sell_qty_per_unit=body.sell_qty_per_unit,
    )
    db.add(product)
    await db.flush()

    # สร้าง stock row พร้อมกันเลย
    db.add(Stock(
        product_id=product.id,
        quantity=body.initial_qty,
        min_qty=body.min_qty,
    ))

    await db.commit()
    return {"id": product.id, "message": "เพิ่มสินค้าเรียบร้อย"}


@router.patch("/{product_id}")
async def update_product(
    product_id: int,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")

    for field, value in body.model_dump(exclude_none=True).items():
        if field == "min_qty":
            stock = await db.execute(select(Stock).where(Stock.product_id == product_id))
            s = stock.scalar_one_or_none()
            if s:
                s.min_qty = value
        else:
            setattr(product, field, value)

    await db.commit()
    return {"message": "อัพเดทเรียบร้อย"}


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    """Soft delete"""
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
    product.deleted_at = datetime.now(timezone.utc)
    product.is_active = False
    await db.commit()
    return {"message": "ลบสินค้าเรียบร้อย"}


# ── Bundle Rules ─────────────────────────────────────────────

@router.get("/{product_id}/bundles")
async def get_bundles(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(
        select(BundleRule).where(
            BundleRule.product_id == product_id,
            BundleRule.is_active.is_(True),
        )
    )
    return result.scalars().all()


@router.post("/{product_id}/bundles")
async def add_bundle(
    product_id: int,
    body: BundleRuleCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    db.add(BundleRule(
        product_id=product_id,
        min_qty=body.min_qty,
        bundle_price=body.bundle_price,
    ))
    await db.commit()
    return {"message": "เพิ่ม bundle rule เรียบร้อย"}


@router.delete("/{product_id}/bundles/{rule_id}")
async def delete_bundle(
    product_id: int,
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    rule = await db.get(BundleRule, rule_id)
    if not rule or rule.product_id != product_id:
        raise HTTPException(status_code=404, detail="ไม่พบ bundle rule")
    rule.is_active = False
    await db.commit()
    return {"message": "ลบ bundle rule เรียบร้อย"}