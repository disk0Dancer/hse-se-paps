from typing import Annotated
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.base import get_async_session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
