from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.cruds.user import get_user_by_email, create_user, verify_password
from app.services.auth import create_access_token
from app.services.auth import get_current_user
from app.models.user import User
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"  # должен совпадать с тем, что при генерации токена
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return {}

router = APIRouter()

@router.get("/users/me/", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sign-up/", response_model=UserOut)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, user)
    token = create_access_token({"sub": user.email})
    return {"id": new_user.id, "email": new_user.email, "token": token}

@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email})
    return {"id": db_user.id, "email": db_user.email, "token": token}
