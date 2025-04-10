from fastapi.testclient import TestClient
from main import app  # Giả sử ứng dụng được lưu trong main.py

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}
    
