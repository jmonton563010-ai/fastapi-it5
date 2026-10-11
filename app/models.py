"""Data models used to validate API input and output."""

from pydantic import BaseModel, Field


class StudentInput(BaseModel):
    """Fields students can send when creating or updating a record."""

    name: str = Field(min_length=1)
    age: int = Field(ge=0)

    @staticmethod
    def list_students(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT id, name, age FROM students ORDER BY id"
            ).fetchall()
        return [rows]

    @staticmethod
    def create_student(student_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO students (name, age) VALUES (?, ?)",
                (student_input.name, student_input.age),
            )
            row = connection.execute(
                "SELECT id, name, age FROM students WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return row

    @staticmethod
    def get_student(student_id, database_connection):
        with database_connection() as connection:
            row = connection.execute(
                "SELECT id, name, age FROM students WHERE id = ?", (student_id,)
            ).fetchone()
        return row

    @staticmethod
    def update_student(student_id, student_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "UPDATE students SET name = ?, age = ? WHERE id = ?",
                (student_input.name, student_input.age, student_id),
            )
            row = connection.execute(
                "SELECT id, name, age FROM students WHERE id = ?", (student_id,)
            ).fetchone()
        return row

    @staticmethod
    def delete_student(student_id, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM students WHERE id = ?", (student_id,)
            )


class Student(StudentInput):
    """A student record returned by the API."""

    id: int
