from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func,case
from database import Base, engine

from fastapi import HTTPException

from fastapi import Depends
from fastapi import Query
from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user, UserCredentials
from security import hash_password, verify_password
from security import create_access_token

from datetime import datetime, date

from models import User, Problem, Resource, Company
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.problems import router as problems_router
Base.metadata.create_all(bind=engine)
    
def resource_to_dic(resource):
    return {
        "id": resource.id,
        "title": resource.title,
        "url": resource.url,
        "topic": resource.topic,
        "notes": resource.notes,
        "created_at": resource.created_at
    }

def company_to_dic(company):
    return {
        "id": company.id,
        "name": company.name,
        "role": company.role,
        "interview format": company.interview_format,
        "application_status": company.application_status,
        "applied on":company.applied_on,
        "status changed on":company.status_updated_at
    }

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(problems_router)

@app.post("/auth/register", status_code=201)
def create_user(credentials: UserCredentials, db: Session = Depends(get_db)):
    try:
        new_user = User(email=credentials.email, hashed_password=hash_password(credentials.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="This Email is already registered")
    

@app.get("/analytics/progress")
def get_progress(current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    week_start = func.subdate(Problem.date_solved, func.dayofweek(Problem.date_solved) - 1)
    records = ( db.query(week_start.label("week_start"), func.count().label("count"))
                .filter(Problem.user_id == current_user.id, Problem.status == "Completed")
                .group_by(week_start) 
                .all() )
    res=[]
    for rec in records:
        ans={}
        ans["week_start"]=rec[0]
        ans["problems_solved"]=rec[1]
        res.append(ans)
    return res

@app.get("/analytics/weak-topics")
def get_weak_topics(current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    completed_count = func.sum(case((Problem.status == "Completed", 1), else_=0))
    records = ( db.query(Problem.topic,completed_count.label("completed"), func.count().label("total"))
                .filter(Problem.user_id == current_user.id)
                .group_by(Problem.topic) 
                .all() )
    res=[]
    for rec in records:
        ans={}
        ans["topic"]=rec[0]
        ans["completed"]=rec[1]
        ans["total"]=rec[2]
        ans["Solve_Rate"]=str(rec[1])+'/'+str(rec[2])
        sp=(rec[1]/rec[2])*100
        ans["Rate"]=sp
        ans["Soved_percentage"]=f"{sp:.2f}%"
        res.append(ans)
    res = sorted(res, key=lambda x: (x["Rate"], x["topic"]))
    for ans in res:
        del ans["Rate"]
    return res


@app.post("/resources", status_code=201)
def create_resources(topic : str,title : str,url : str,notes : str, current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    new_resource=Resource(user_id=current_user.id, topic=topic, title=title, url=url, notes=notes)
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return {"id":new_resource.id,"title":new_resource.title}

@app.get("/resources")
def get_resource(current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    query=db.query(Resource).filter(Resource.user_id==current_user.id)
    records=query.all()
    return [resource_to_dic(p) for p in records]

@app.delete("/resources/{id}")
def delete_resource(id : int,current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    resource=db.query(Resource).filter(Resource.id==id,Resource.user_id==current_user.id).first()
    if resource:
        title_val=resource.title
        db.delete(resource)
        db.commit()
        return f"The Resource {title_val} has been deleted"
    else:
        raise HTTPException(status_code=404, detail="Resource Not Found")

@app.post("/companies", status_code=201)
def create_companies(name : str,role : str,interview_format : str,application_status : str = Query(..., description="Valid choices: Applied, Interviewing, Offer Received, Accepted, Rejected"), current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    VALID_APPLICATION_STATUSES = ["Applied", "Interviewing", "Offer Received", "Accepted", "Rejected"]
    if application_status not in VALID_APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid application_status. Valid choices are: {VALID_APPLICATION_STATUSES}")
    if not name:
        raise HTTPException(status_code=400, detail="Company name cannot be empty")
    if not role:
        raise HTTPException(status_code=400, detail="Role cannot be empty")
    if not interview_format:
        raise HTTPException(status_code=400, detail="Interviewing Format should not be empty")
    new_company=Company(user_id=current_user.id, name=name, role=role, interview_format=interview_format, application_status=application_status)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return {"id":new_company.id,"Company name":new_company.name}

@app.get("/companies")
def get_company(current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    query=db.query(Company).filter(Company.user_id==current_user.id)
    records=query.all()
    return [company_to_dic(p) for p in records]

@app.put("/companies/{id}")
def update_company(id : int,role:str=None,interview_format:str=None,application_status : str = Query(None, description="Valid choices: Applied, Interviewing, Offer Received, Accepted, Rejected"),current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    VALID_APPLICATION_STATUSES = ["Applied", "Interviewing", "Offer Received", "Accepted", "Rejected"]
    if application_status and (application_status not in VALID_APPLICATION_STATUSES):
        raise HTTPException(status_code=400, detail=f"Invalid application_status. Valid choices are: {VALID_APPLICATION_STATUSES}")

    company=db.query(Company).filter(Company.id==id,Company.user_id==current_user.id).first()
    if company:
        if role:
            company.role=role
        if interview_format:
            company.interview_format=interview_format
        if application_status:
            company.application_status=application_status
            company.status_updated_at = datetime.now()
        db.commit()
        return company_to_dic(company)
    else:
        raise HTTPException(status_code=404, detail="Company Not Found")

