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


#======Delete Response Schema =====
class DeleteResponse(BaseModel):
    message: str

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

# ===== Resource Schemas =====
class CreateResourceRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Topic cannot be empty")
    title: str = Field(..., min_length=1, description="Title cannot be empty")
    url: str = Field(..., min_length=1, description="URL cannot be empty")
    notes: Optional[str] = None


class ResourceResponse(BaseModel):
    id: int
    topic: str
    title: str
    url: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Company Schemas =====
class CreateCompanyRequest(BaseModel):
    name: str = Field(..., min_length=2, description="Company name cannot be empty")
    role: str = Field(..., min_length=2, description="Role cannot be empty")
    interview_format: str = Field(..., min_length=2, description="Interview format cannot be empty")
    application_status: ApplicationStatusEnum


class UpdateCompanyRequest(BaseModel):
    role: Optional[str] = None
    interview_format: Optional[str] = None
    application_status: Optional[ApplicationStatusEnum] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    role: str
    interview_format: str
    application_status: str
    applied_on: datetime
    status_updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ===== Analytics Schemas =====
class ProgressResponse(BaseModel):
    week_start: Optional[date]
    problems_solved: int


class WeakTopicResponse(BaseModel):
    topic: str
    completed: int
    total: int
    Solve_Rate: str
    Soved_percentage: str