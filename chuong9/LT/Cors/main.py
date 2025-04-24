from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả domain truy cập (không an toàn, chỉ dùng khi phát triển)
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả phương thức (GET, POST, PUT, DELETE, ...)
    allow_headers=["*"],  # Cho phép tất cả headers
)

#Nếu nhu bạn muốn có vài ddieeuf kiện thì đây là ví dụ
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://example.com", "https://myapp.com"],  # Chỉ cho phép các domain này
#     allow_credentials=True,
#     allow_methods=["GET", "POST"],  # Chỉ cho phép GET và POST
#     allow_headers=["Authorization", "Content-Type"],  # Chỉ cho phép các header cụ thể
# )

@app.get("/")
async def home():
    return {"message": "API đã bật CORS!"}

