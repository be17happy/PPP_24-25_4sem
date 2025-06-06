from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# --- SQLAlchemy настройка ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- Модели ---
class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    author = relationship("Author", back_populates="books")

# --- Pydantic-схемы ---

# Author (для вывода)
class AuthorOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# Author (для создания/обновления)
class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

# Book (для вывода)
class BookOut(BaseModel):
    id: int
    title: str
    year: int
    author_id: int

    class Config:
        orm_mode = True
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# --- Зависимость для сессии ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Эндпоинты для Authors ---

@app.get("/authors", response_model=List[AuthorOut])
def list_authors(db: Session = Depends(get_db)):
    authors = db.query(Author).all()
    return authors

@app.post("/authors", response_model=AuthorOut, status_code=201)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = Author(name=author.name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

@app.get("/authors/{author_id}", response_model=AuthorOut)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author
@app.put("/authors/{author_id}", response_model=AuthorOut)
def update_author(author_id: int, author_data: AuthorCreate, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    author.name = author_data.name
    db.commit()
    db.refresh(author)
    return author

@app.delete("/authors/{author_id}", status_code=204)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(author)
    db.commit()
    return None  # Возвращаем пустой ответ (No Content)

# Book (для создания)
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    year: int = Field(..., ge=0, le=2100)
    author_id: int
# --- Эндпоинты для Books ---

# Список книг (опционально фильтруется по author_id)
@app.get("/books", response_model=List[BookOut])
def list_books(author_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Book)
    if author_id is not None:
        query = query.filter(Book.author_id == author_id)
    return query.all()

# Создать книгу
@app.post("/books", response_model=BookOut, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    # Проверка что автор существует
    author = db.query(Author).filter(Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db_book = Book(
        title=book.title,
        year=book.year,
        author_id=book.author_id
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# --- Создание таблиц ---
Base.metadata.create_all(bind=engine)

# --- Простейшая ручка для проверки ---
@app.get("/ping")
def ping():
    return {"status": "ok"}
