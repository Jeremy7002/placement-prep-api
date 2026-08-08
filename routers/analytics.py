from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, case

from database import get_db
from models import User, Problem
from security import get_current_user

router = APIRouter()


@router.get("/analytics/progress")
def get_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    week_start = func.subdate(Problem.date_solved, func.dayofweek(Problem.date_solved) - 1)
    records = (db.query(week_start.label("week_start"), func.count().label("count"))
               .filter(Problem.user_id == current_user.id, Problem.status == "Completed")
               .group_by(week_start)
               .all())
    res = []
    for rec in records:
        ans = {}
        ans["week_start"] = rec[0]
        ans["problems_solved"] = rec[1]
        res.append(ans)
    return res


@router.get("/analytics/weak-topics")
def get_weak_topics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completed_count = func.sum(case((Problem.status == "Completed", 1), else_=0))
    records = (db.query(Problem.topic, completed_count.label("completed"), func.count().label("total"))
               .filter(Problem.user_id == current_user.id)
               .group_by(Problem.topic)
               .all())
    res = []
    for rec in records:
        ans = {}
        ans["topic"] = rec[0]
        ans["completed"] = rec[1]
        ans["total"] = rec[2]
        ans["Solve_Rate"] = str(rec[1]) + '/' + str(rec[2])
        sp = (rec[1] / rec[2]) * 100
        ans["Rate"] = sp
        ans["Soved_percentage"] = f"{sp:.2f}%"
        res.append(ans)
    res = sorted(res, key=lambda x: (x["Rate"], x["topic"]))
    for ans in res:
        del ans["Rate"]
    return res