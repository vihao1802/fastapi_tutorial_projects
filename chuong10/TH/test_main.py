from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_student():
    response = client.post("/students/", json={"id": 1, "name": "Alice", "age": 20})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 20}

def test_get_students():
    response = client.get("/students/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_student():
    response = client.get("/students/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

def test_update_student():
    response = client.put("/students/1", json={"id": 1, "name": "Alice Updated", "age": 21})
    assert response.status_code == 200
    assert response.json()["name"] == "Alice Updated"

def test_delete_student():
    response = client.delete("/students/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Student deleted"}

def test_get_deleted_student():
    response = client.get("/students/1")
    assert response.status_code == 404
