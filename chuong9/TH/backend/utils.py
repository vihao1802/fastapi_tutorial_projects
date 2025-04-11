import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

def generate_qr_code(url: str):
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")
