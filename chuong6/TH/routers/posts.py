from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select, func
from typing import Annotated
from database import get_session
from models.user import User
from models.post import Post
from datetime import datetime
import datetime
import shutil
import os

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

SessionDep = Annotated[Session, Depends(get_session)]

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Tạo thư mục nếu chưa có


@router.post("/")
def create_post(
    session: SessionDep,
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
    author_id: str = Form(...),
):
    # Kiểm tra xem người dùng có tồn tại không
    author = session.get(User, int(author_id))
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    image_path = None
    if image:
        file_location = f"{UPLOAD_DIR}/{image.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = f"/{file_location}"  # Lưu đường dẫn

    post_data = Post(
        title=title,
        content=content,
        image=image_path,
        author_id=int(author_id),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )

    session.add(post_data)
    session.commit()
    session.refresh(post_data)
    return {
        "status_code": 201,
        "detail": "Post created successfully",
        "post": post_data,
    }


@router.get("")
def get_posts(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 10
):
    posts = session.exec(select(Post).offset(offset).limit(limit)).all()
    return [
        {
            "id": post.id,
            "title": post.title,
            "image": post.image,
            "content": post.content,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "author": (
                {"id": post.author.id, "name": post.author.username}
                if post.author
                else None
            ),
        }
        for post in posts
    ]


@router.get("/{post_id}")
def get_post(post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/user/{user_id}")
def get_posts_by_user(
    user_id: int,
    session: SessionDep,
    title: None | str = None,
    content: None | str = None,
    created_at: None | str = None,
):
    query = select(Post).where(Post.author_id == user_id)

    if title:
        query = query.where(Post.title.contains(title))
    if content:
        query = query.where(Post.content.contains(content))
    if created_at:
        try:
            created_date = datetime.strptime(created_at, "%Y-%m-%d").date()
            query = query.where(func.date(Post.created_at) == created_date)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
            )

    posts = session.exec(query).all()
    return posts


@router.patch("/{post_id}")
async def update_post(
    session: SessionDep,
    post_id: int,
    title: None | str = Form(None),
    content: None | str = Form(None),
    image: None | UploadFile = File(None),
):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Cập nhật từng trường nếu có dữ liệu
    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    if image:
        file_location = f"{UPLOAD_DIR}/{image.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        post.image = f"/{file_location}"  # Cập nhật đường dẫn ảnh

    post.updated_at = datetime.datetime.now()  # Cập nhật thời gian

    session.add(post)
    session.commit()
    session.refresh(post)

    return {
        "status_code": 200,
        "detail": "Post updated successfully",
        "post": post,
    }


@router.delete("/{post_id}")
def delete_post(post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    session.delete(post)
    session.commit()
    return {
        "status_code": 200,
        "detail": "Post deleted successfully",
    }
