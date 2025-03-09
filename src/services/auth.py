from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import select

from src.models.user import User
from src.models.access_token import AccessToken
from src.dependencies import SessionDep
from src.services.settings import settings

ALGORITHM = "HS256"
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime  # Added expiration time for client-side refresh logic
    refresh_token: Optional[str] = None  # Optional refresh token


# Token Factory - A GoF Factory pattern implementation
class TokenFactory:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Factory method to create JWT access tokens"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, expire  # Return both the token and expiration time

    @staticmethod
    def create_refresh_token(data: dict):
        """Create a refresh token with a longer expiration time"""
        to_encode = data.copy()
        # Refresh tokens typically last longer than access tokens
        refresh_expires = datetime.now(timezone.utc) + timedelta(days=7)  # 7 days
        to_encode.update({"exp": refresh_expires, "refresh": True})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, refresh_expires


# Facade pattern - providing simplified interface to token verification
class AuthService:
    _token_from_request = None  # Store the current request's token

    @staticmethod
    async def get_current_user(
        session: SessionDep, token: str = Depends(oauth2_scheme)
    ):
        """Verify token and return current user"""
        # Store the token for potential later use in the request lifecycle
        AuthService._token_from_request = token

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode and verify token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)

            # Check if this is a refresh token - they can't be used for authentication
            if payload.get("refresh"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token cannot be used for authentication",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except jwt.PyJWTError:
            raise credentials_exception

        # Check if token is revoked
        token_stmt = select(AccessToken).where(
            AccessToken.token == token, AccessToken.is_revoked is True
        )
        result = await session.execute(token_stmt)
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_stmt = select(AccessToken).where(
            AccessToken.token == token, AccessToken.end_timestamp < datetime.utcnow()
        )
        result = await session.execute(token_stmt)
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        statement = select(User).where(User.login == token_data.username)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception

        return user

    @staticmethod
    def create_token(user: User) -> Token:
        """Create JWT token for user with auto-refresh capabilities"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, expires_at = TokenFactory.create_access_token(
            data={"sub": user.login}, expires_delta=access_token_expires
        )
        refresh_token, _ = TokenFactory.create_refresh_token(data={"sub": user.login})

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at,
            refresh_token=refresh_token,
        )

    @staticmethod
    def get_token_from_request() -> str:
        """Get the token used in the current request"""
        return AuthService._token_from_request

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify a token and return its payload

        Args:
            token: The token to verify

        Returns:
            The decoded payload

        Raises:
            HTTPException: If the token is invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
