from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Problem
from schemas import CreateProblemRequest, UpdateProblemRequest, StatusEnum


class ProblemService:

    @staticmethod
    def create(db: Session, user_id: int, data: CreateProblemRequest) -> Problem:
        new_problem = Problem(
            user_id=user_id,
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

    @staticmethod
    def get_all(db: Session, user_id: int, topic: str = None, status: str = None) -> list[Problem]:
        query = db.query(Problem).filter(Problem.user_id == user_id)
        if topic:
            query = query.filter(func.lower(Problem.topic) == topic.strip().lower())
        if status:
            try:
                status_enum = StatusEnum(status)
                query = query.filter(Problem.status == status_enum.value)
            except ValueError:
                raise ValueError(f"Invalid status. Valid choices are: {[s.value for s in StatusEnum]}")
        return query.all()

    @staticmethod
    def get_by_id(db: Session, id: int, user_id: int) -> Problem | None:
        return db.query(Problem).filter(Problem.id == id, Problem.user_id == user_id).first()

    @staticmethod
    def update(db: Session, problem: Problem, data: UpdateProblemRequest) -> Problem:
        if data.status:
            problem.status = data.status.value
        if data.date_solved:
            problem.date_solved = data.date_solved
        db.commit()
        db.refresh(problem)
        return problem

    @staticmethod
    def delete(db: Session, problem: Problem) -> None:
        db.delete(problem)
        db.commit()