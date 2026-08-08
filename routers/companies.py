from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import User, Company
from security import get_current_user

router = APIRouter()


def company_to_dic(company):
    return {
        "id": company.id,
        "name": company.name,
        "role": company.role,
        "interview format": company.interview_format,
        "application_status": company.application_status,
        "applied on": company.applied_on,
        "status changed on": company.status_updated_at
    }


@router.post("/companies", status_code=201)
def create_companies(name: str, role: str, interview_format: str, application_status: str = Query(..., description="Valid choices: Applied, Interviewing, Offer Received, Accepted, Rejected"), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    VALID_APPLICATION_STATUSES = ["Applied", "Interviewing", "Offer Received", "Accepted", "Rejected"]
    if application_status not in VALID_APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid application_status. Valid choices are: {VALID_APPLICATION_STATUSES}")
    if not name:
        raise HTTPException(status_code=400, detail="Company name cannot be empty")
    if not role:
        raise HTTPException(status_code=400, detail="Role cannot be empty")
    if not interview_format:
        raise HTTPException(status_code=400, detail="Interviewing Format should not be empty")
    new_company = Company(user_id=current_user.id, name=name, role=role, interview_format=interview_format, application_status=application_status)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return {"id": new_company.id, "Company name": new_company.name}


@router.get("/companies")
def get_company(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Company).filter(Company.user_id == current_user.id)
    records = query.all()
    return [company_to_dic(p) for p in records]


@router.put("/companies/{id}")
def update_company(id: int, role: str = None, interview_format: str = None, application_status: str = Query(None, description="Valid choices: Applied, Interviewing, Offer Received, Accepted, Rejected"), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    VALID_APPLICATION_STATUSES = ["Applied", "Interviewing", "Offer Received", "Accepted", "Rejected"]
    if application_status and (application_status not in VALID_APPLICATION_STATUSES):
        raise HTTPException(status_code=400, detail=f"Invalid application_status. Valid choices are: {VALID_APPLICATION_STATUSES}")

    company = db.query(Company).filter(Company.id == id, Company.user_id == current_user.id).first()
    if company:
        if role:
            company.role = role
        if interview_format:
            company.interview_format = interview_format
        if application_status:
            company.application_status = application_status
            company.status_updated_at = datetime.now()
        db.commit()
        return company_to_dic(company)
    else:
        raise HTTPException(status_code=404, detail="Company Not Found")