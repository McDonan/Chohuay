from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.services import ServiceCreate

from core.database import get_db
from core.dependencies import get_current_user
from models.service import ServiceTransaction

router = APIRouter()

@router.post("/")
async def create_service(
    body: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),   # staff ทำได้
):
    db.add(ServiceTransaction(
        type=body.type,
        amount=body.amount,
        fee=body.fee,
        note=body.note,
        created_by=user["id"],
    ))
    await db.commit()
    return {"message": "บันทึกรายการเรียบร้อย"}


@router.get("/")
async def list_services(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(
        select(ServiceTransaction).order_by(ServiceTransaction.created_at.desc()).limit(50)
    )
    return result.scalars().all()