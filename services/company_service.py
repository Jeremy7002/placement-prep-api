from sqlalchemy.orm import Session
from datetime import datetime

from models import Company
from schemas import CreateCompanyRequest, UpdateCompanyRequest


class CompanyService:

    @staticmethod
    def create(db: Session, user_id: int, data: CreateCompanyRequest) -> Company:
        new_company = Company(
            user_id=user_id,
            name=data.name,
            role=data.role,
            interview_format=data.interview_format,
            application_status=data.application_status
        )
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        return new_company

    @staticmethod
    def get_all(db: Session, user_id: int) -> list[Company]:
        return db.query(Company).filter(Company.user_id == user_id).all()

    @staticmethod
    def get_by_id(db: Session, id: int, user_id: int) -> Company | None:
        return db.query(Company).filter(Company.id == id, Company.user_id == user_id).first()

    @staticmethod
    def update(db: Session, company: Company, data: UpdateCompanyRequest) -> Company:
        if data.role:
            company.role = data.role
        if data.interview_format:
            company.interview_format = data.interview_format
        if data.application_status:
            company.application_status = data.application_status
            company.status_updated_at = datetime.now()
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def delete(db: Session, company: Company) -> None:
        db.delete(company)
        db.commit()