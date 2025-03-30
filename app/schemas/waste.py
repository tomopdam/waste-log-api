from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.waste import WasteType


# WasteLog schemas
class WasteLogBase(BaseModel):
    waste_type: WasteType
    weight_kg: float
    description: Optional[str] = None


class WasteLogCreate(WasteLogBase):
    pass


class WasteLogUpdate(BaseModel):
    waste_type: Optional[WasteType] = None
    weight_kg: Optional[float] = None
    description: Optional[str] = None


class WasteLogRead(WasteLogBase):
    id: int
    team_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
