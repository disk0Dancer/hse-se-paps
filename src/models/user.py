from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship


class UserBase(SQLModel):
    login: str = Field(index=True)
    password: str


class User(UserBase, table=True):
    guid: int | None = Field(default=None, primary_key=True)
    # Establish relationship to AccessToken model
    access_tokens: List["AccessToken"] = Relationship(back_populates="user")


class UserPublic(UserBase):
    guid: int


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    login: Optional[str] = None
    password: Optional[str] = None


def generate_user_token(user):
    return user.login + "token"
