from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, Optional
from sqlmodel import Session, select

from src.models.user import User, UserCreate, UserUpdate

router = APIRouter()


@router.post("/user/", response_model=User)
def create_user(user: UserCreate, session: Session = Depends(...)) -> User:
    session.add(User(**user.dict()))
    session.commit()
    session.refresh(user)
    return user


@router.get("/user/", response_model=list[User])
def read_users(
    session: Session = Depends(...),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/user/search", response_model=list[User])
def search_users(
    login: Optional[str] = None,
    session: Session = Depends(...),
):
    if not login:
        return []
    # Example search
    statement = select(User).where(User.login.contains(login))
    results = session.exec(statement).all()
    return results


@router.get("/user/{user_id}", response_model=User)
def read_user(user_id: int, session: Session = Depends(...)) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/user/{user_id}", response_model=User)
def update_user(
    user_id: int, user_update: UserUpdate, session: Session = Depends(...)
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/user/{user_id}")
def delete_user(user_id: int, session: Session = Depends(...)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
