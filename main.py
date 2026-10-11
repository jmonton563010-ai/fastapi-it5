import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

DATABASE_URL = "sqlite:///./library_system.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    books = relationship("BookModel", back_populates="borrower")

class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    is_borrowed = Column(Boolean, default=False)
    borrower_id = Column(Integer, ForeignKey("students.id"), nullable=True)

    borrower = relationship("StudentModel", back_populates="books")

Base.metadata.create_all(bind=engine)

class StudentInput(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)
    email: EmailStr

class StudentResponse(StudentInput):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookInput(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)

class BookResponse(BookInput):
    id: int
    is_borrowed: bool
    borrower_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

app = FastAPI(title="Library Resource Management System")

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Welcome to the Library Management System API!"}

@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentInput, db: Session = Depends(get_db)):
    db_student = StudentModel(name=student.name, age=student.age, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students", response_model=List[StudentResponse], tags=["Students"])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(StudentModel).all()

@app.get("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def update_student(student_id: int, updated_data: StudentInput, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.name = updated_data.name
    student.age = updated_data.age
    student.email = updated_data.email
    db.commit()
    db.refresh(student)
    return student

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return None

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book: BookInput, db: Session = Depends(get_db)):
    db_book = BookModel(title=book.title, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books", response_model=List[BookResponse], tags=["Books"])
def get_all_books(db: Session = Depends(get_db)):
    return db.query(BookModel).all()

@app.post("/books/{book_id}/borrow/{student_id}", response_model=BookResponse, tags=["Transactions"])
def borrow_book(book_id: int, student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.is_borrowed:
        raise HTTPException(status_code=400, detail="Book is already checked out by another student")
    book.is_borrowed = True
    book.borrower_id = student.id
    db.commit()
    db.refresh(book)
    return book

@app.post("/books/{book_id}/return", response_model=BookResponse, tags=["Transactions"])
def return_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.is_borrowed:
        raise HTTPException(status_code=400, detail="Book was not checked out")
    book.is_borrowed = False
    book.borrower_id = None
    db.commit()
    db.refresh(book)
    return book

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
