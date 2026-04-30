from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id         : Mapped[int]      = mapped_column(primary_key=True)
    name       : Mapped[str]      = mapped_column(String(100))
    pin_hash   : Mapped[str]      = mapped_column(String(255))
    role       : Mapped[str]      = mapped_column(String(20))   # owner | staff
    is_active  : Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
