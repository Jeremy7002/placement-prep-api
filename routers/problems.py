from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User
from security import get_current_user
from schemas import CreateProblemRequest, UpdateProblemRequest, ProblemResponse, DeleteResponse
from services.problem_service import ProblemService

router = APIRouter()


@router.post("/problems", status_code=201, response_model=ProblemResponse)
def create_problems(data: CreateProblemRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProblemService.create(db, current_user.id, data)


@router.get("/problems", response_model=list[ProblemResponse])
def get_problem(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), topic: Optional[str] = None, status: Optional[str] = None):
    return ProblemService.get_all(db, current_user.id, topic, status)


@router.put("/problems/{id}", response_model=ProblemResponse)
def update_problem(id: int, data: UpdateProblemRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = ProblemService.get_by_id(db, id, current_user.id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem Not Found")
    return ProblemService.update(db, problem, data)


@router.delete("/problems/{id}", response_model=DeleteResponse)
def delete_problem(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = ProblemService.get_by_id(db, id, current_user.id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem Not Found")
    id_val = problem.id
    ProblemService.delete(db, problem)
    return {"message": f"The Record of id:{id_val} has been deleted"}