from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, Optional, List
from sqlmodel import select
from src.models.user import User, UserCreate, UserUpdate, UserResponse
from src.services.auth import AuthService
from src.dependencies import SessionDep

router = APIRouter()

@router.post("/user/", response_model=UserResponse)
async def create_user(session: SessionDep, user: UserCreate) -> UserResponse:
    db_user = User(**user.dict())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.get("/user/", response_model=List[UserResponse])
async def read_users(
    session: SessionDep,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[UserResponse]:
    statement = select(User).offset(offset).limit(limit)
    results = await session.execute(statement)
    users = results.scalars().all()
    return users

@router.get("/user/search", response_model=List[UserResponse])
async def search_users(
    session: SessionDep,
    login: Optional[str] = None,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
) -> List[UserResponse]:
    if not login:
        return []
    statement = select(User).where(User.login.contains(login))
    results = await session.execute(statement)
    users = results.scalars().all()
    return users

@router.get("/user/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    session: SessionDep,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
) -> UserResponse:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/user/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: SessionDep,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
) -> UserResponse:
    user = await session.get(User, user_id)
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

@router.delete("/user/{user_id}")
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: User = Depends(AuthService.get_current_user),  # Protected route
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.guid != current_user.guid:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this user"
        )

    await session.delete(user)
    await session.commit()
    return {"ok": True}