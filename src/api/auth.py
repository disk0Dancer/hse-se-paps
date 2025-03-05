from sqlmodel import select
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.models.user import User, UserResponse
from src.services.auth import AuthService, Token
from src.models.access_token import AccessToken
from src.dependencies import SessionDep

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
):
    user_stmt = select(User).where(User.login == form_data.username)
    user = session.exec(user_stmt).first()

    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = AuthService.create_token(user)
    expires = datetime.utcnow() + timedelta(minutes=30)
    db_token = AccessToken(
        user_guid=user.guid,
        token=token.access_token,
        start_timestamp=datetime.utcnow(),
        end_timestamp=expires,
    )
    session.add(db_token)
    session.commit()
    return token


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(AuthService.get_current_user)):
    return current_user
