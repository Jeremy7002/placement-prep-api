from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum


# ===== Enums =====
class StatusEnum(str, Enum):
    COMPLETED = "Completed"
    NOT_COMPLETED = "Not Completed"
    PENDING = "Pending"


class DifficultyEnum(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class ApplicationStatusEnum(str, Enum):
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFER_RECEIVED = "Offer Received"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


# ===== Auth Schemas =====
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Problem Schemas =====
class CreateProblemRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="Topic cannot be empty")
    title: str = Field(..., min_length=2, description="Title cannot be empty")
    difficulty: DifficultyEnum
    status: StatusEnum
    date_solved: date


class UpdateProblemRequest(BaseModel):
    status: Optional[StatusEnum] = None
    date_solved: Optional[date] = None


class ProblemResponse(BaseModel):
    id: int
    topic: str
    title: str
    status: str
    difficulty: str
    date_solved: date

    class Config:
        from_attributes = True
