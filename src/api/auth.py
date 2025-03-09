from sqlmodel import select
from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Body
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
    """Get access and refresh tokens by providing username and password"""
    user_stmt = select(User).where(User.login == form_data.username)
    user = await session.execute(user_stmt)
    user = user.scalar_one_or_none()

    # Using the secure verification method
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token with refresh capabilities
    token = AuthService.create_token(user)

    # Store both access and refresh tokens in the database
    db_token = AccessToken(
        guid=str(uuid.uuid4()),
        user_guid=user.guid,
        token=token.access_token,
        refresh_token=token.refresh_token,
        start_timestamp=datetime.utcnow(),
        end_timestamp=token.expires_at,
        refresh_end_timestamp=datetime.utcnow() + timedelta(days=7),  # 7 days
    )
    session.add(db_token)
    await session.commit()
    return token


@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(
    session: SessionDep, refresh_token: str = Body(..., embed=True)
):
    """Generate new access and refresh tokens using a refresh token"""
    try:
        # Verify the refresh token
        payload = AuthService.verify_token(refresh_token)

        # Check if it's actually a refresh token
        if not payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload"
            )

        # Find the token in the database
        token_stmt = select(AccessToken).where(
            AccessToken.refresh_token == refresh_token
        )
        result = await session.execute(token_stmt)
        db_token = result.scalar_one_or_none()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token not found",
            )

        # Check if token is revoked
        if db_token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        # Check if refresh token has expired
        if db_token.refresh_end_timestamp < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )

        # Get the user
        user_stmt = select(User).where(User.login == username)
        result = await session.execute(user_stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
            )

        # Revoke the old token
        db_token.is_revoked = True
        session.add(db_token)

        # Generate new tokens
        new_token = AuthService.create_token(user)

        # Store the new tokens in the database
        new_db_token = AccessToken(
            guid=str(uuid.uuid4()),
            user_guid=user.guid,
            token=new_token.access_token,
            refresh_token=new_token.refresh_token,
            start_timestamp=datetime.utcnow(),
            end_timestamp=new_token.expires_at,
            refresh_end_timestamp=datetime.utcnow() + timedelta(days=7),  # 7 days
        )
        session.add(new_db_token)
        await session.commit()

        return new_token

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to refresh token: {str(e)}",
        )


@router.post("/token/revoke")
async def revoke_token(
    session: SessionDep, current_user: User = Depends(AuthService.get_current_user)
):
    """Revoke the current token"""
    # Get the token from the AuthService
    token = AuthService.get_token_from_request()

    # Find and revoke the token in the database
    token_stmt = select(AccessToken).where(AccessToken.token == token)
    result = await session.execute(token_stmt)
    db_token = result.scalar_one_or_none()

    if db_token:
        db_token.is_revoked = True
        session.add(db_token)
        await session.commit()
        return {"message": "Token successfully revoked"}

    return {"message": "Token not found"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(AuthService.get_current_user)):
    return current_user
