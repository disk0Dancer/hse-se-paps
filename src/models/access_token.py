from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from .base import Base


class AccessToken(Base):
    __tablename__ = "access_tokens"

    guid = Column(String(36), primary_key=True, unique=True, index=True, nullable=False)
    user_guid = Column(
        String(36), ForeignKey("users.guid", ondelete="CASCADE"), nullable=False
    )
    token = Column(String, unique=True, index=True, nullable=False)
    start_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_timestamp = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    user = relationship("User", back_populates="access_tokens")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

    class Config:
        from_attributes = True
