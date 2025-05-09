from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)  # Chạy request
    process_time = time.time() - start_time
    print(f"{request.method} {request.url} - {response.status_code} - {process_time:.4f}s")
    return response

@app.get("/")
async def home():
    return {"message": "Xin chào!"}