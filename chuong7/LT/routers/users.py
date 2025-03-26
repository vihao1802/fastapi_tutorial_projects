from fastapi import APIRouter, Depends, HTTPException, Query
from configs.database import get_session
from models.user import User, UserCreate
from sqlmodel import  Session, select
from typing import Annotated

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/")
def create(user: UserCreate, session: SessionDep):
    user = User.from_orm(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/")
def read_all(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/{id}")
def read(id: int, session: SessionDep) -> User:
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user

@router.delete("/{id}")
def delete(id: int, session: SessionDep):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    session.delete(user)
    session.commit()
    return {"ok": True}