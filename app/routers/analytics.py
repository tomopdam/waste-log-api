from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.auth import enforce_team_id_for_user, get_current_active_manager
from app.db.session import get_session
from app.exceptions import ResourceNotFoundError
from app.models.team import Team
from app.models.user import User
from app.models.waste import WasteLog, WasteType
from app.schemas.analytics import TeamWasteSummary
from app.schemas.waste import WasteLogRead

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/team-logs", response_model=List[WasteLogRead])
async def read_waste_logs_by_team(
    team_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_manager),
):
    team_id = enforce_team_id_for_user(team_id, current_user)

    # Check if team exists
    team = session.get(Team, team_id)
    if not team:
        raise ResourceNotFoundError("Team", str(team_id))

    # Filter by team, apply offset and limit
    query = (
        select(WasteLog).where(WasteLog.team_id == team_id).offset(skip).limit(limit)
    )

    logs = session.exec(query).all()
    return logs


@router.get("/team-summary", response_model=TeamWasteSummary)
async def get_team_analytics(
    team_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_manager),
):
    team_id = enforce_team_id_for_user(team_id, current_user)
    # Check if team exists
    team = session.get(Team, team_id)
    if not team:
        raise ResourceNotFoundError("Team", str(team_id))

    # Get total entries
    total_entries_result = session.exec(
        select(func.count(WasteLog.id)).where(WasteLog.team_id == team_id)
    ).first()

    total_entries = (
        total_entries_result if total_entries_result and total_entries_result else 0
    )

    # Get total waste kg
    total_weight_result = session.exec(
        select(func.sum(WasteLog.weight_kg).label("total")).where(
            WasteLog.team_id == team_id
        )
    ).first()

    total_waste_kg = (
        total_weight_result if total_weight_result and total_weight_result else 0
    )

    # Get waste by type
    waste_by_type = {}
    for waste_type in WasteType:
        type_result = session.exec(
            select(func.sum(WasteLog.weight_kg).label("total"))
            .where(WasteLog.team_id == team_id)
            .where(WasteLog.waste_type == waste_type)
        ).first()

        waste_by_type[waste_type] = type_result if type_result and type_result else 0.0

    # Get recent entries
    recent_logs = session.exec(
        select(WasteLog)
        .where(WasteLog.team_id == team_id)
        .order_by(WasteLog.created_at.desc())
        .limit(10)
    ).all()

    # cast to appropriate return schema
    recent_entries = [WasteLogRead.model_validate(log) for log in recent_logs]

    return TeamWasteSummary(
        total_entries=total_entries,
        total_waste_kg=total_waste_kg,
        waste_by_type=waste_by_type,
        recent_entries=recent_entries,
    )
