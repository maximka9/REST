# app/api/user.py

from fastapi import Request  
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse  
from app.db.db import get_db
from app.utils import verify_password, get_password_hash
from app.core.auth import get_current_user, invalidate_token, oauth2_scheme  
from slowapi import Limiter 
from slowapi.util import get_remote_address  

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)  

@router.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse.from_orm(new_user)

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = jwt.encode({"sub": db_user.id}, os.getenv("JWT_SECRET"), algorithm="HS256")
    
    return TokenResponse(access_token=token, token_type="bearer")

@router.post("/logout")
@limiter.limit("100/minute")  # Ограничение на 100 запросов в минуту
def logout(request: Request, token: str = Depends(oauth2_scheme)):
    invalidate_token(token)
    return {"detail": "Successfully logged out"}
