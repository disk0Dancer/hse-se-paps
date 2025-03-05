from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import select

from src.models.user import User
from src.dependencies import SessionDep

# Secret key for JWT signing - in production, store this in environment variables
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


# Token Factory - A GoF Factory pattern implementation
class TokenFactory:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Factory method to create JWT access tokens"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


# Facade pattern - providing simplified interface to token verification
class AuthService:
    @staticmethod
    async def get_current_user(
        session: SessionDep, token: str = Depends(oauth2_scheme)
    ):
        """Verify token and return current user"""
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
        except jwt.PyJWTError:
            raise credentials_exception

        # Look up the user in the database
        statement = select(User).where(User.login == token_data.username)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception

        return user

    @staticmethod
    def create_token(user: User) -> Token:
        """Create JWT token for user"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = TokenFactory.create_access_token(
            data={"sub": user.login}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
