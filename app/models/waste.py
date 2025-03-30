from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.helpers import utc_now
from app.models.team import Team
from app.models.user import User


class WasteType(str, Enum):
    PAPER = "paper"
    PLASTIC = "plastic"
    GLASS = "glass"
    METAL = "metal"
    ORGANIC = "organic"
    ELECTRONIC = "electronic"
    OTHER = "other"


class WasteLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    waste_type: WasteType
    weight_kg: float
    description: Optional[str] = None

    # Relationships
    team_id: int = Field(foreign_key="team.id", index=True)
    team: Team = Relationship(back_populates="waste_logs")

    created_by_id: int = Field(foreign_key="user.id", index=True)
    created_by: User = Relationship(back_populates="waste_logs")

    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
