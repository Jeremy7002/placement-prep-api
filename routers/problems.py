from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from models import User, Problem
from security import get_current_user

router = APIRouter()


def rec_to_dic(problem):
    return {
        "id": problem.id,
        "topic": problem.topic,
        "title": problem.title,
        "status": problem.status,
        "difficulty": problem.difficulty,
        "date_solved": problem.date_solved
    }


@router.post("/problems", status_code=201)
def create_problems(topic: str, title: str, difficulty: str = Query(..., description="Valid choices: Easy, Medium, Hard"), status: str = Query(..., description="Valid choices: Completed, Not Completed, Pending"), date_solved: date = Query(..., description="Format: YYYY-MM-DD"), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    VALID_STATUSES = ["Completed", "Not Completed", "Pending"]
    VALID_DIFFICULTIES = ["Easy", "Medium", "Hard"]
    if not topic:
        raise HTTPException(status_code=400, detail="Topic should not be empty")
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid choices are: {VALID_STATUSES}")
    if difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty. Valid choices are: {VALID_DIFFICULTIES}")
    new_problem = Problem(user_id=current_user.id, topic=topic, title=title, difficulty=difficulty, status=status, date_solved=date_solved)
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return {"id": new_problem.id, "title": new_problem.title}


@router.get("/problems")
def get_problem(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), topic: str = None, status: str = Query(None, description="Valid choices: Completed, Not Completed, Pending")):
    query = db.query(Problem).filter(Problem.user_id == current_user.id)
    if topic:
        query = query.filter(Problem.topic == topic)
    if status:
        query = query.filter(Problem.status == status)
    records = query.all()
    return [rec_to_dic(p) for p in records]


@router.put("/problems/{id}")
def update_problem(id: int, status: str = Query(None, description="Valid choices: Completed, Not Completed, Pending"), date_solved: date = Query(None, description="Format: YYYY-MM-DD"), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    VALID_STATUSES = ["Completed", "Not Completed", "Pending"]
    if status and (status not in VALID_STATUSES):
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid choices are: {VALID_STATUSES}")

    problem = db.query(Problem).filter(Problem.id == id, Problem.user_id == current_user.id).first()
    if problem:
        if status:
            problem.status = status
        if date_solved:
            problem.date_solved = date_solved
        db.commit()
        return rec_to_dic(problem)
    else:
        raise HTTPException(status_code=404, detail="Problem Not Found")


@router.delete("/problems/{id}")
def delete_problem(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == id, Problem.user_id == current_user.id).first()
    if problem:
        id_val = problem.id
        db.delete(problem)
        db.commit()
        return f"The Record of id:{id_val} has been deleted"
    else:
        raise HTTPException(status_code=404, detail="Problem Not Found")