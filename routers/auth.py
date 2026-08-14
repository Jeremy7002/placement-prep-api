from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import User
from security import hash_password, verify_password, create_access_token
from schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/auth/register", status_code=201, response_model=UserResponse)
def create_user(credentials: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        new_user = User(email=credentials.email, hashed_password=hash_password(credentials.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="This Email is already registered")


@router.post("/auth/login", response_model=TokenResponse)
def login_check(credentials: UserLoginRequest, db: Session = Depends(get_db)):
    check_for_email = db.query(User).filter(User.email == credentials.email).first()
    if check_for_email is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    hashed = check_for_email.hashed_password
    check_for_pass = verify_password(credentials.password, hashed)
    if check_for_pass:
        payload = str(check_for_email.id)
        token = create_access_token({"sub": payload})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid Credentials")