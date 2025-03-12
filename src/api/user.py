from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, List
from sqlmodel import select
from src.models.user import User, UserCreate, UserUpdate, UserResponse
from src.services.auth import AuthService
from src.dependencies import SessionDep
import uuid

# from src.models.access_token import AccessToken

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(session: SessionDep, user: UserCreate) -> UserResponse:
    user_dict = user.dict()
    user_dict["guid"] = str(uuid.uuid4())  # Generate a unique GUID
    db_user = User(**user_dict)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserResponse])
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[UserResponse]:
    statement = select(User).offset(offset).limit(limit)
    results = await session.execute(statement)
    users = results.scalars().all()
    return users


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    session: SessionDep, current_user: User = Depends(AuthService.get_current_user)
):
    """
    Get the current user's details.
    Returns profile and all access tokens.
    """
    # statement = select(AccessToken).where(AccessToken.user_guid == current_user.guid)
    # results = await session.execute(statement)
    # current_user.access_tokens = results.scalars().all()
    return current_user


@router.get("/{user_guid}", response_model=UserResponse)
async def read_user(
    user_guid: str,
    session: SessionDep,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
) -> UserResponse:
    statement = select(User).where(User.guid == user_guid)
    results = await session.execute(statement)
    user = results.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_guid}", response_model=UserResponse)
async def update_user(
    user_guid: str,
    user_update: UserUpdate,
    session: SessionDep,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
) -> UserResponse:
    statement = select(User).where(User.guid == user_guid)
    results = await session.execute(statement)
    user = results.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.guid != current_user.guid:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this user"
        )

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_guid}")
async def delete_user(
    user_guid: str,
    session: SessionDep,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
):
    statement = select(User).where(User.guid == user_guid)
    results = await session.execute(statement)
    user = results.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.guid != current_user.guid:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this user"
        )

    await session.delete(user)
    await session.commit()
    return {"ok": True}
