from fastapi import APIRouter,HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
router = APIRouter()

@router.post("/auth/login")
def login_check(credentials: UserCredentials, db: Session = Depends(get_db)):
    check_for_email=db.query(User).filter(User.email == credentials.email).first()
    if check_for_email is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    hashed=check_for_email.hashed_password
    check_for_pass=verify_password(credentials.password,hashed)
    if check_for_pass:
        payload=str(check_for_email.id)
        token = create_access_token({"sub":payload})
        return {"access_token": token, "token_type": "bearer"}        
    else:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
