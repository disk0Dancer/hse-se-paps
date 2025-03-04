from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class AccessToken(SQLModel, table=True):
    guid: int | None = Field(default=None, primary_key=True)
    user_guid: int = Field(foreign_key="user.guid")
    token: str
    start_timestamp: datetime
    end_timestamp: datetime

    # Relationship back to User
    user: Optional["User"] = Relationship(back_populates="access_tokens")
