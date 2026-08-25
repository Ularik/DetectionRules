from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime, func
from src.database import Base
from datetime import datetime
from enum import Enum


class UserRoles(Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[bytes]
    role: Mapped[UserRoles] = mapped_column(default=UserRoles.VIEWER, server_default=UserRoles.VIEWER.value)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.timezone('Asia/Bishkek', func.now()))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone('Asia/Bishkek', func.now()),
        onupdate=func.timezone('Asia/Bishkek', func.now())
    )

