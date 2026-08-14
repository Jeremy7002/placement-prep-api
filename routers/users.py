from fastapi import APIRouter, Depends

from models import User
from security import get_current_user
from schemas import UserResponse

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
def get_users(current_user: User = Depends(get_current_user)):
    return current_user