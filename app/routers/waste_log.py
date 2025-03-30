from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.auth import (
    enforce_team_id_for_user,
    get_current_active_admin,
    get_current_active_employee,
    get_current_active_manager,
    get_current_user,
)
from app.db.session import get_session
from app.exceptions import AuthorizationError, ResourceNotFoundError
from app.models.user import User, UserRole
from app.models.waste import WasteLog
from app.schemas.waste import WasteLogCreate, WasteLogRead, WasteLogUpdate

router = APIRouter(prefix="/waste-logs", tags=["waste-logs"])


@router.post("/", response_model=WasteLogRead, status_code=status.HTTP_201_CREATED)
async def create_waste_log(
    log_data: WasteLogCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_employee),
    team_id: Optional[int] = None,
):
    team_id = enforce_team_id_for_user(team_id, current_user)
    db_log = WasteLog(
        **log_data.model_dump(), team_id=team_id, created_by_id=current_user.id
    )

    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


@router.get("/", response_model=List[WasteLogRead])
async def read_all_waste_logs(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    query = select(WasteLog).offset(skip).limit(limit)

    logs = session.exec(query).all()
    return logs


@router.get("/{log_id}", response_model=WasteLogRead)
async def read_waste_log(
    log_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    log = session.get(WasteLog, log_id)
    if not log:
        raise ResourceNotFoundError("WasteLog", str(log_id))

    # Check authorization
    if current_user.role == UserRole.ADMIN:
        pass
    elif current_user.role == UserRole.MANAGER and current_user.team_id == log.team_id:
        pass
    elif current_user.id == log.created_by_id:
        pass
    else:
        raise AuthorizationError("You do not have permission to view that log")

    return log


@router.patch("/{log_id}", response_model=WasteLogRead)
async def update_waste_log(
    log_id: int,
    log_data: WasteLogUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    log = session.get(WasteLog, log_id)
    if not log:
        raise ResourceNotFoundError("WasteLog", str(log_id))

    if current_user.role == UserRole.ADMIN:
        pass
    else:
        raise AuthorizationError("You do not have permission to modify that log")

    # Update log data
    update_data = log_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(log, key, value)

    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_waste_log(
    log_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    log = session.get(WasteLog, log_id)
    if not log:
        raise ResourceNotFoundError("WasteLog", str(log_id))

    if current_user.role == UserRole.ADMIN:
        pass
    else:
        raise AuthorizationError("You do not have permission to delete that log")

    session.delete(log)
    session.commit()
    return None
