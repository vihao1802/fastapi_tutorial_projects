from sqlmodel import SQLModel, Field, Relationship
from typing import List


class UserBase(SQLModel):
    username: str = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    posts: List["Post"] = Relationship(back_populates="author")


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    username: str | None = None
    password: str | None = None
