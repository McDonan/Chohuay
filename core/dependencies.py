from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import decode_token

bearer = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_token(creds.credentials)
        return {"id": int(payload["sub"]), "role": payload["role"]}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ไม่ถูกต้อง")

async def require_owner(user=Depends(get_current_user)):
    if user["role"] != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าของร้านเท่านั้น")
    return user
