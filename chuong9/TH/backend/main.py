from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import io
import time
import re
from pydantic import BaseModel

app = FastAPI()

# 1. Cấu hình CORS đúng
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc ['http://localhost:5500']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Biến lưu thời gian truy cập theo IP để chống spam
request_times = {}

class RequestBody(BaseModel):
    url: str
    
# 2. Middleware chống spam và kiểm tra URL hợp lệ
@app.middleware("http")
async def validate_url_and_prevent_spam(request: Request, call_next):
    if request.method == "OPTIONS":
        # Cho phép preflight request đi qua (CORS)
        return await call_next(request)

    if request.url.path == "/generate_qr":
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})

        url = body.get("url", "")
        ip = request.client.host

        # Regex kiểm tra URL hợp lệ
        url_pattern = re.compile(r'^https?://[\w\-\.]+\.[a-z]{2,}(/\S*)?$')
        if not url_pattern.match(url):
            return JSONResponse(status_code=400, content={"error": "Invalid URL format"})

        # Chống spam theo IP trong 10 giây
        now = time.time()
        if ip not in request_times:
            request_times[ip] = []
        # Lọc chỉ giữ lại các request trong 10 giây gần nhất
        request_times[ip] = [t for t in request_times[ip] if now - t < 10]
        request_times[ip].append(now)

        if len(request_times[ip]) > 3:
            return JSONResponse(status_code=429, content={"error": "Too many requests. Please wait."})

    # Nếu mọi thứ ổn, tiếp tục xử lý request
    return await call_next(request)


# 3. Endpoint generate QR
@app.post("/generate_qr")
async def generate_qr(request: RequestBody):
    img = qrcode.make(request.url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
