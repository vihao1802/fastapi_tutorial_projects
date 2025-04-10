from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

class Student(BaseModel):
    id: int
    name: str
    age: int

students_db = []

@app.post("/students/", response_model=Student)
def create_student(student: Student):
    logger.debug(f"Received request to create student: {student}")
    for s in students_db:
        if s.id == student.id:
            logger.warning(f"Duplicate student ID detected: {student.id}")
            raise HTTPException(status_code=400, detail="Student already exists")
    students_db.append(student)
    logger.info(f"Student created: {student}")
    return student

@app.get("/students/", response_model=List[Student])
def get_students():
    logger.debug(students_db)
    return students_db

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    logger.debug(f"Looking for student with ID: {student_id}")
    for student in students_db:
        if student.id == student_id:
            logger.info(f"Student found: {student}")
            return student
    logger.error(f"Student not found with ID: {student_id}")
    raise HTTPException(status_code=404, detail="Student not found")

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, updated_student: Student):
    logger.debug(f"Updating student ID {student_id} with data: {updated_student}")
    for idx, student in enumerate(students_db):
        if student.id == student_id:
            students_db[idx] = updated_student
            logger.info(f"Student updated: {updated_student}")
            return updated_student
    logger.error(f"Update failed. Student not found with ID: {student_id}")
    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    logger.debug(f"Request to delete student with ID: {student_id}")
    for student in students_db:
        if student.id == student_id:
            students_db.remove(student)
            logger.info(f"Student deleted: {student}")
            return {"message": "Student deleted"}
    logger.error(f"Deletion failed. Student not found with ID: {student_id}")
    raise HTTPException(status_code=404, detail="Student not found")
