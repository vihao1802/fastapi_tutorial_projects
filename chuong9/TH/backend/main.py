from fastapi import FastAPI, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from middleware import LogRequestMiddleware, URLValidationMiddleware, RateLimitMiddleware
import qrcode
from io import BytesIO

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware
app.add_middleware(LogRequestMiddleware)
app.add_middleware(URLValidationMiddleware)
app.add_middleware(RateLimitMiddleware)

@app.post("/generate")
async def generate_qr(url: str = Form(...)):
    # In ra log kiểm tra nhận form data
    print("Received URL:", url)
    
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")
