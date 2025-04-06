from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager
from configs.database import  create_db_and_tables
from routers.cart import router as cart_router
from routers.order import router as order_router

# asynccontextmanager can define logic (code) that should be executed once, before the application starts receiving requests.
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can specify a list of allowed domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Serve static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

app.include_router(cart_router)
app.include_router(order_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to FastAPI!",
        "docs": "http://127.0.0.1:8000/docs",
        "home": "http://localhost:8000/home"
    }

# Endpoint serving index.html
@app.get("/home")
def read_index():
    return FileResponse("static/index.html")

# Endpoint serving index.html
@app.get("/payment/order/{order_id}")
def read_payment():
    return FileResponse("static/payment.html")