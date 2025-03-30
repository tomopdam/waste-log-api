from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.auth import authenticate_user, create_access_token
from app.config import settings
from app.db.session import get_session
from app.exceptions import AuthenticationError
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise AuthenticationError("Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id},
        expires_delta=access_token_expires,
    )

    # Store token in database for potential invalidation
    user.auth_token = access_token
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"access_token": access_token, "token_type": "bearer"}
