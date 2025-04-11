from fastapi import FastAPI
import pdb
import logging
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hsello, FastAPI!"}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/debug")
def debug_endpoint():
    x= 100;
    y= 200;
    z= x+y;
    logger.info("Debugging FastAPI!")
    logger.debug(f"X: {x}, Y: {y}, Z: {z}")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    return {"message": "Debugging FastAPI!"}

@app.get("/test")
def test_debug():
    x= 100;
    y= 200;
    z= x+y;
    pdb.set_trace()  # Dừng tại đây để kiểm tra biến
    return {"message": "Testing debug"}