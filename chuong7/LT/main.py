from typing import Annotated
from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from configs.database import get_session, create_db_and_tables
from routers.users import router as user_router

# asynccontextmanager can define logic (code) that should be executed once, before the application starts receiving requests.
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to FastAPI!",
        "docs": "http://127.0.0.1:8000/docs"
    }