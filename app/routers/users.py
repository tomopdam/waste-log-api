from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.auth import (
    get_current_active_admin,
    get_current_active_employee,
    get_current_user,
    get_password_hash,
)
from app.db.session import get_session
from app.exceptions import AuthorizationError, ResourceNotFoundError, ValidationError
from app.models.team import Team
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    # Validate team assignment based on role
    if user_data.role == UserRole.ADMIN and user_data.team_id:
        raise ValidationError("Admin users cannot be assigned to a team")

    if (
        user_data.role in [UserRole.EMPLOYEE, UserRole.MANAGER]
        and not user_data.team_id
    ):
        raise ValidationError("Employees and managers must be assigned to a team")

    # Check if team exists if team_id provided
    if user_data.team_id:
        team = session.get(Team, user_data.team_id)
        if not team:
            raise ResourceNotFoundError("Team", str(user_data.team_id))

    # Create user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        team_id=user_data.team_id,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.get("/me", response_model=UserRead)
async def read_user_me(current_user: User = Depends(get_current_active_employee)):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_employee),
):
    # Allow users to access their own data
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise AuthorizationError()

    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", str(user_id))

    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", str(user_id))

    # Update user data
    update_data = user_data.model_dump(exclude_unset=True)

    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    # Validate team assignment based on role
    if "role" in update_data and update_data["role"] == UserRole.ADMIN:
        update_data["team_id"] = None

    if "role" in update_data and update_data["role"] in [
        UserRole.EMPLOYEE,
        UserRole.MANAGER,
    ]:
        if "team_id" in update_data and update_data["team_id"] is None:
            raise ValidationError("Employees and managers must be assigned to a team")
        elif "team_id" not in update_data and user.team_id is None:
            raise ValidationError("Employees and managers must be assigned to a team")

    # Check if team exists if team_id provided
    if "team_id" in update_data and update_data["team_id"] is not None:
        team = session.get(Team, update_data["team_id"])
        if not team:
            raise ResourceNotFoundError("Team", str(update_data["team_id"]))

    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", str(user_id))

    session.delete(user)
    session.commit()
    return None


@router.post("/{user_id}/invalidate-token", status_code=status.HTTP_200_OK)
async def invalidate_user_token(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_admin),
):
    user = session.get(User, user_id)
    if not user:
        raise ResourceNotFoundError("User", str(user_id))

    # Invalidate token
    user.auth_token = None
    session.add(user)
    session.commit()

    return {"message": f"User {user.username} token invalidated successfully"}
