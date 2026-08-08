from fastapi import APIRouter, Depends

from models import User
from security import get_current_user

router = APIRouter()


@router.get("/users/me")
def get_users(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }