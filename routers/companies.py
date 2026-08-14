from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import User, Company
from security import get_current_user
from schemas import CreateCompanyRequest, UpdateCompanyRequest, CompanyResponse, DeleteResponse, ApplicationStatusEnum

router = APIRouter()


@router.post("/companies", status_code=201, response_model=CompanyResponse)
def create_companies(data: CreateCompanyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_company = Company(
        user_id=current_user.id,
        name=data.name,
        role=data.role,
        interview_format=data.interview_format,
        application_status=data.application_status
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company


@router.get("/companies", response_model=list[CompanyResponse])
def get_company(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(Company).filter(Company.user_id == current_user.id).all()
    return records


@router.put("/companies/{id}", response_model=CompanyResponse)
def update_company(id: int, data: UpdateCompanyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == id, Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company Not Found")
    
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


@router.delete("/companies/{id}", response_model=DeleteResponse)
def delete_company(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == id, Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company Not Found")
    
    company_name = company.name
    db.delete(company)
    db.commit()
    return {"message": f"The Company {company_name} has been deleted"}