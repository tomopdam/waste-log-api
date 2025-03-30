from typing import List

from pydantic import BaseModel, create_model

from app.models.waste import WasteType
from app.schemas.waste import WasteLogRead

# create a pydantic model to display the waste_by_type dictionary schema
WasteByType = create_model(
    "WasteByType",
    __config__=type("Config", (), {"extra": "forbid"}),
    **{wt.value: (float, 0.0) for wt in WasteType},
)


# Analytics schemas
class TeamWasteSummary(BaseModel):
    total_entries: int
    total_waste_kg: float
    waste_by_type: WasteByType
    recent_entries: List[WasteLogRead]
