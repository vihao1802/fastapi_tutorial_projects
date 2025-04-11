from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import re, time
from urllib.parse import urlparse

rate_limit_cache = {}

class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        process_time = time.time() - start
        print(f"[LOG] {request.client.host} - {request.method} {request.url.path} in {process_time:.3f}s")
        return response

class URLValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method == "POST" and request.url.path == "/generate":
            # Lưu trữ body để sử dụng lại
            body = await request.body()
            # Tạo form từ body đã lưu
            form = await request.form()
            url = form.get("url")
            parsed_url = urlparse(url) if url is not None else None
            if not parsed_url or not parsed_url.scheme or not parsed_url.netloc:
                return JSONResponse(status_code=400, content={"error": "Invalid URL"})
            
            # Sau khi đọc body, ta phải "reset" lại stream cho downstream.
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive  # Gán lại hàm receive cho request
        return await call_next(request)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = time.time()
        window = 10  # seconds
        max_requests = 5

        if ip not in rate_limit_cache:
            rate_limit_cache[ip] = []
        recent = [t for t in rate_limit_cache[ip] if now - t < window]
        if len(recent) >= max_requests:
            return Response("Too many requests", status_code=429)
        recent.append(now)
        rate_limit_cache[ip] = recent
        return await call_next(request)
