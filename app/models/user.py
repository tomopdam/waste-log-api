from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.helpers import utc_now
from app.models.team import Team


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(unique=True)
    full_name: Optional[str] = None
    hashed_password: str

    role: UserRole

    # Optional team relationship (admins don't have a team)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", index=True)
    team: Optional[Team] = Relationship(back_populates="users")

    # Auth token for invalidation
    auth_token: Optional[str] = None

    # Relationships
    waste_logs: List["WasteLog"] = Relationship(back_populates="created_by")

    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
