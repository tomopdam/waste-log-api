from datetime import timedelta
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.config import settings
from app.db.session import get_session
from app.exceptions import AuthenticationError, AuthorizationError
from app.helpers import utc_now
from app.models.user import User, UserRole
from app.schemas.auth import TokenData

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def authenticate_user(session: Session, username: str, password: str):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = utc_now() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.API_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.API_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = session.exec(
        select(User).where(User.username == token_data.username)
    ).first()
    if user is None:
        raise credentials_exception

    # Check if token has been invalidated
    if user.auth_token != token:
        raise AuthenticationError("Session expired. Please login again.")

    return user


async def get_current_active_employee(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.ADMIN]:
        raise AuthorizationError("Invalid role")
    return current_user


async def get_current_active_manager(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise AuthorizationError("Manager or admin role required")
    return current_user


async def get_current_active_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError("Admin role required")
    return current_user


def enforce_team_id_for_user(team_id: Optional[int], current_user: User) -> int:
    """
    Enforces that the team_id provided matches the user's team_id, or that
    they are an admin and have provided a team_id.
    """
    # admin override
    if current_user.role == UserRole.ADMIN:
        if team_id is None:
            raise AuthorizationError("Admins must provide a team_id")
        return team_id
    # manager or employee
    if team_id is not None and team_id != current_user.team_id:
        raise AuthorizationError("You are not a member of that team")
    # If team_id is None, return the user's team_id
    if team_id is None:
        team_id = current_user.team_id
    return team_id
