from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.auth import ChangePinRequest, LoginRequest, LoginResponse

from core.security import verify_pin, create_token, hash_pin
from core.dependencies import get_current_user
from core.database import get_db
from models.user import User

router = APIRouter()

@router.post("/change-pin")
async def change_pin(
    body: ChangePinRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user["id"]))
    db_user = result.scalar_one_or_none()
    if not db_user or not verify_pin(body.old_pin, db_user.pin_hash):
        raise HTTPException(status_code=401, detail="รหัส PIN เดิมไม่ถูกต้อง")
    if len(body.new_pin) < 4:
        raise HTTPException(status_code=400, detail="PIN ใหม่ต้องมีอย่างน้อย 4 หลัก")
    db_user.pin_hash = hash_pin(body.new_pin)
    await db.commit()
    return {"message": "เปลี่ยน PIN สำเร็จ"}



@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.is_active.is_(True)))
    users = result.scalars().all()

    for user in users:
        if verify_pin(body.pin, user.pin_hash):
            token = create_token(user.id, user.role)
            return LoginResponse(access_token=token, role=user.role, name=user.name)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="PIN ไม่ถูกต้อง"
    )