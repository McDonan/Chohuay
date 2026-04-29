from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date
from typing import Optional

from core.database import get_db
from core.dependencies import require_owner

router = APIRouter()

@router.get("/daily")
async def daily_report(
    start: Optional[date] = None,
    end:   Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    """รายงานกำไร/รายได้รายวัน"""
    query = "SELECT * FROM daily_summary"
    conditions = []
    params = {}
    if start:
        conditions.append("sale_date >= :start")
        params["start"] = start
    if end:
        conditions.append("sale_date <= :end")
        params["end"] = end
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY sale_date DESC LIMIT 30"

    result = await db.execute(text(query), params)
    return result.mappings().all()

@router.get("/low-stock")
async def low_stock(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    result = await db.execute(text("SELECT * FROM low_stock_alert"))
    return result.mappings().all()

@router.get("/top-products")
async def top_products(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_owner),
):
    """สินค้าขายดี 7 วันล่าสุด"""
    result = await db.execute(text("""
        SELECT
            p.name,
            SUM(si.qty)                             AS total_qty,
            SUM(si.qty * si.unit_price)             AS total_revenue,
            SUM(si.qty * (si.unit_price - si.unit_cost)) AS total_profit
        FROM sale_items si
        JOIN products p ON p.id = si.product_id
        JOIN sales s    ON s.id = si.sale_id
        WHERE s.cancelled_at IS NULL
          AND s.created_at >= NOW() - INTERVAL '1 day' * :days
        GROUP BY p.id, p.name
        ORDER BY total_qty DESC
        LIMIT 10
    """), {"days": days})
    return result.mappings().all()