import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Cho phép frontend truy cập
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response model
class UploadResponse(BaseModel):
    public_id: str
    file_name: str
    url: str
    format: str
    size: int


# custom error handler
class InvalidFileFormatException(Exception):
    def __init__(self, file_format: str):
        self.file_format = file_format


@app.exception_handler(InvalidFileFormatException)
async def invalid_file_format_handler(
    request: Request, exc: InvalidFileFormatException
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": f"Invalid file format: {exc.file_format}. Only jpg, jpeg, png, gif allowed."
        },
    )


# **Xử lý lỗi: Request Validation Error**
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid input data", "errors": exc.errors()},
    )


# **Xử lý lỗi: HTTPException chung**
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Upload file
@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    allowed_formats = {"png", "jpg", "jpeg", "gif"}
    file_extension = file.filename.split(".")[-1]

    if file_extension not in allowed_formats:
        raise InvalidFileFormatException(file_format=file_extension)
    try:
        response = cloudinary.uploader.upload(
            file.file, folder=os.getenv("CLOUDINARY_FOLDER")
        )
        upload_response = {
            "public_id": response["public_id"],
            "file_name": response["original_filename"],
            "url": response["url"],
            "format": response["format"],
            "size": response["bytes"],
        }
        return UploadResponse(**upload_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# **API Xóa ảnh trên Cloudinary**
@app.delete("/delete")
async def delete_file(public_id: str = Query(...)):
    try:
        print(public_id)
        result = cloudinary.uploader.destroy(public_id)
        if result["result"] != "ok":
            raise HTTPException(status_code=400, detail="Failed to delete image")
        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/images/", response_model=list[UploadResponse])
async def get_images():
    try:
        result = cloudinary.api.resources(
            type="upload", prefix=os.getenv("CLOUDINARY_FOLDER"), max_results=100
        )
        images = [
            UploadResponse(
                public_id=img["public_id"],
                file_name=img["public_id"].split("/")[-1],  # Lấy tên file từ public_id
                url=img["secure_url"],
                format=img["format"],
                size=img["bytes"],
            )
            for img in result["resources"]
        ]
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch images: {str(e)}")
