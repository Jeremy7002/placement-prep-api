from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import (
    CreateProblemRequest,
    DeleteResponse,
    ProblemResponse,
    UpdateProblemRequest,
)
from security import get_current_user
from services.problem_service import ProblemService

router = APIRouter()


@router.post("/problems", status_code=201, response_model=ProblemResponse)
def create_problem(
    data: CreateProblemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProblemService.create(db, current_user.id, data)


@router.get("/problems", response_model=list[ProblemResponse])
def list_problems(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    topic: Optional[str] = None,
    status: Optional[str] = None,
):
    return ProblemService.get_all(db, current_user.id, topic, status)


@router.put("/problems/{id}", response_model=ProblemResponse)
def update_problem(
    id: int,
    data: UpdateProblemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    problem = ProblemService.get_by_id(db, id, current_user.id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem Not Found")
    return ProblemService.update(db, problem, data)


@router.delete("/problems/{id}", response_model=DeleteResponse)
def delete_problem(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    problem = ProblemService.get_by_id(db, id, current_user.id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem Not Found")
    ProblemService.delete(db, problem)
    return {"message": f"Problem {id} deleted"}
