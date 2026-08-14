from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database import get_db
from models import User, Problem
from security import get_current_user
from schemas import CreateProblemRequest, UpdateProblemRequest, ProblemResponse, StatusEnum

router = APIRouter()


@router.post("/problems", status_code=201, response_model=ProblemResponse)
def create_problems(data: CreateProblemRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_problem = Problem(
        user_id=current_user.id,
        topic=data.topic.strip().title(),
        title=data.title,
        difficulty=data.difficulty,
        status=data.status,
        date_solved=data.date_solved
    )
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return new_problem

@router.get("/problems", response_model=list[ProblemResponse])
def get_problem(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), topic: Optional[str] = None, status: Optional[str] = None):
    query = db.query(Problem).filter(Problem.user_id == current_user.id)
    if topic:
        query = query.filter(func.lower(Problem.topic) == topic.strip().lower())
    if status:
        try:
            status_enum = StatusEnum(status)
            query = query.filter(Problem.status == status_enum.value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status. Valid choices are: {[s.value for s in StatusEnum]}")
    records = query.all()
    return records


@router.put("/problems/{id}", response_model=ProblemResponse)
def update_problem(id: int, data: UpdateProblemRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == id, Problem.user_id == current_user.id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem Not Found")
    
    if data.status:
        problem.status = data.status.value
    if data.date_solved:
        problem.date_solved = data.date_solved
    db.commit()
    db.refresh(problem)
    return problem

@router.delete("/problems/{id}")
def delete_problem(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == id, Problem.user_id == current_user.id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem Not Found")
    
    id_val = problem.id
    db.delete(problem)
    db.commit()
    return {"message": f"The Record of id:{id_val} has been deleted"}