from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str
    team_id: Optional[int] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    team_id: Optional[int] = None
    password: Optional[str] = None


class UserRead(UserBase):
    id: int
    team_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
