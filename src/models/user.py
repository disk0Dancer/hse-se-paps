from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    guid = Column(String(36), primary_key=True, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    login = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationships
    access_tokens = relationship(
        "AccessToken", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, value):
        self.hashed_password = str(hash(value))

    def validate_password(self, password: str) -> bool:
        return str(hash(password)) == self.hashed_password


# Pydantic models for API
class UserBase(BaseModel):
    email: EmailStr
    login: str
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str

    @validator("password")
    def password_validation(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    login: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    guid: str
    created_at: datetime
    updated_at: datetime
