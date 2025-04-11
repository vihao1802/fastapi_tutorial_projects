from fastapi import FastAPI
from routers import auth
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

app = FastAPI()

app.include_router(auth.router, prefix="/auth")

app.get('/')
async def root():
    return {"message": "Hello World"}
