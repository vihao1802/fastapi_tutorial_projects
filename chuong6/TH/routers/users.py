from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Annotated

from database import get_session

from models.user import User, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/")
def create_user(user: User, session: SessionDep):
    existing_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    session.add(user)
    session.commit()
    session.refresh(user)
    return {
        "status_code": 201,
        "detail": "User created successfully",
        "user": user,
    }


@router.post("/login")
def login_user(user: User, session: SessionDep):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "status_code": 200,
        "detail": "Login successful",
        "user": db_user,
    }


@router.get("/")
def get_users(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 10
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}")
def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for attr, value in user_update.dict(exclude_unset=True).items():
        setattr(user, attr, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return {
        "status_code": 200,
        "detail": "User updated successfully",
        "user": user,
    }
