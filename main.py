"""Create the FastAPI app and connect its route modules."""

from fastapi import FastAPI

from app.database import database_connection, initialize_database
from app.models import Student, StudentInput

app = FastAPI(title="Beginner Student API")


@app.get("/")
def home():
    return {"message": "Welcome! Visit /docs to try the API."}


@app.get("/students")
def get_students():
    result = Student.list_students(database_connection=database_connection)
    return {"students": result}


@app.get("/students/{student_id}")
def get_student(student_id: int):
    result = Student.get_student(
        student_id=student_id, database_connection=database_connection
    )
    return {"student": result}


@app.post("/student")
def create_student(student: StudentInput):
    result = Student.create_student(
        student_input=student, database_connection=database_connection
    )
    return {"student": result}


@app.put("/student/{student_id}")
def edit_student(student_id: int, student: Student):
    result = Student.update_student(
        student_id=student_id,
        student_input=student,
        database_connection=database_connection,
    )
    return {"student": result}


@app.delete("/student/{student_id}")
def delete_student(student_id: int):
    Student.delete_student(
        student_id=student_id, database_connection=database_connection
    )
    return {"message": "Student deleted successfully"}


initialize_database()
