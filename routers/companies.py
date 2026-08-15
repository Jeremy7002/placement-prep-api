from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from security import get_current_user
from schemas import CreateCompanyRequest, UpdateCompanyRequest, CompanyResponse, DeleteResponse
from services.company_service import CompanyService

router = APIRouter()


@router.post("/companies", status_code=201, response_model=CompanyResponse)
def create_companies(data: CreateCompanyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CompanyService.create(db, current_user.id, data)


@router.get("/companies", response_model=list[CompanyResponse])
def get_company(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CompanyService.get_all(db, current_user.id)


@router.put("/companies/{id}", response_model=CompanyResponse)
def update_company(id: int, data: UpdateCompanyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = CompanyService.get_by_id(db, id, current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company Not Found")
    return CompanyService.update(db, company, data)


@router.delete("/companies/{id}", response_model=DeleteResponse)
def delete_company(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = CompanyService.get_by_id(db, id, current_user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company Not Found")
    company_name = company.name
    CompanyService.delete(db, company)
    return {"message": f"The Company {company_name} has been deleted"}