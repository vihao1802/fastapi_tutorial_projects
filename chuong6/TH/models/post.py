from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import List, Optional


class PostBase(SQLModel):
    title: str = Field(index=True, nullable=False)
    image: str | None = Field(default=None, nullable=True)
    content: str = Field(nullable=False)


class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Dùng forward reference để tránh vòng lặp import
    author: Optional["User"] = Relationship(back_populates="posts")


class PostCreate(PostBase):
    author_id: int


class PostUpdate(PostBase):
    title: str | None = None
    image: str | None = None
    content: str | None = None
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
