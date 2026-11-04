from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, case

from database import get_db
from models import User, Problem
from security import get_current_user
from schemas import ProgressResponse, WeakTopicResponse

router = APIRouter()


@router.get("/analytics/progress", response_model=list[ProgressResponse])
def get_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    week_start = func.subdate(Problem.date_solved, func.dayofweek(Problem.date_solved) - 1)
    records = (db.query(week_start.label("week_start"), func.count().label("problems_solved"))
               .filter(Problem.user_id == current_user.id, Problem.status == "Completed")
               .group_by(week_start)
               .all())
    return records


@router.get("/analytics/weak-topics", response_model=list[WeakTopicResponse])
def get_weak_topics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completed_count = func.sum(case((Problem.status == "Completed", 1), else_=0))
    records = (db.query(Problem.topic, completed_count.label("completed"), func.count().label("total"))
               .filter(Problem.user_id == current_user.id)
               .group_by(Problem.topic)
               .all())

    scored = []
    for rec in records:
        topic, completed, total = rec[0], rec[1], rec[2]
        percentage = (completed / total) * 100 if total else 0.0
        scored.append((percentage, topic, completed, total))

    scored.sort(key=lambda row: (row[0], row[1]))

    res = []
    for percentage, topic, completed, total in scored:
        res.append({
            "topic": topic,
            "completed": completed,
            "total": total,
            "Solve_Rate": f"{completed}/{total}",
            "Soved_percentage": f"{percentage:.2f}%",
        })
    return res
