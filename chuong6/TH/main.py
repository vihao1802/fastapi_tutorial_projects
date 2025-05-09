from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from database import create_db_and_tables
from contextlib import asynccontextmanager
from routers import posts, users
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép frontend truy cập
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)

# Mount thư mục static
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/login")
def read_index():
    return FileResponse("static/auth.html")


@app.get("/home")
def read_index():
    return FileResponse("static/home.html")


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
