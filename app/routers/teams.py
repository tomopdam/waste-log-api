from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.auth import (
    get_current_active_admin,
    get_current_active_manager,
    get_current_user,
)
from app.db.session import get_session
from app.exceptions import AuthorizationError, ResourceNotFoundError, ValidationError
from app.models.team import Team
from app.models.user import User, UserRole
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    db_team = Team(name=team_data.name)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@router.get("/", response_model=List[TeamRead])
async def read_teams(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_manager),
):
    # Admins can see all teams
    if current_user.role == UserRole.ADMIN:
        teams = session.exec(select(Team).offset(skip).limit(limit)).all()
    # Managers and employees can only see their own team
    else:
        if current_user.team_id is None:
            return []
        teams = [session.get(Team, current_user.team_id)]

    return teams


@router.get("/{team_id}", response_model=TeamRead)
async def read_team(
    team_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_manager),
):
    # Check authorization
    if current_user.role != UserRole.ADMIN and current_user.team_id != team_id:
        raise AuthorizationError()

    team = session.get(Team, team_id)
    if not team:
        raise ResourceNotFoundError("Team", str(team_id))

    return team


@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    team = session.get(Team, team_id)
    if not team:
        raise ResourceNotFoundError("Team", str(team_id))

    # Update team data
    update_data = team_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(team, key, value)

    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    team = session.get(Team, team_id)
    if not team:
        raise ResourceNotFoundError("Team", str(team_id))

    # Check if team has users
    users = session.exec(select(User).where(User.team_id == team_id)).all()
    if users:
        raise ValidationError("Cannot delete team with assigned users")

    session.delete(team)
    session.commit()
    return None
