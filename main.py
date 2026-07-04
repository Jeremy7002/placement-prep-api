from fastapi import FastAPI

from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Enum,Date,Text
from sqlalchemy.sql import func,case
from sqlalchemy.exc import IntegrityError
from database import Base, engine

from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from fastapi import Query
from sqlalchemy.orm import Session

from database import SessionLocal

from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone,date

import os
from dotenv import load_dotenv

load_dotenv()
security=HTTPBearer()
password_hash = PasswordHash.recommended()
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic=Column(String(255))
    title=Column(String(255))
    status = Column(Enum("Not Completed", "Pending", "Completed", name="status_enum"))
    difficulty=Column(Enum("Hard", "Medium", "Easy", name="difficulty_enum"))
    date_solved=Column(Date)

class Resource(Base):
    __tablename__="resources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title=Column(String(255))
    url=Column(String(500))
    topic=Column(String(255))
    notes=Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class Company(Base):
    __tablename__="companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name=Column(String(255))
    role=Column(String(255))
    interview_format=Column(String(255))
    application_status = Column(Enum("Applied", "Interviewing", "Offer Received", "Accepted", "Rejected", name="application_status_enum"))
    applied_on = Column(DateTime, server_default=func.now())
    status_updated_at = Column(DateTime)

Base.metadata.create_all(bind=engine)
    
def rec_to_dic(problem):
    return {
        "id": problem.id,
        "topic": problem.topic,
        "title": problem.title,
        "status": problem.status,
        "difficulty": problem.difficulty,
        "date_solved": problem.date_solved
    }

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/about-me")
def about_me():
    return {"name": "<your-name>"}

@app.get("/ping")
def return_pong():
    return {"message":"pong"}

@app.get("/users")
def get_users(db:Session=Depends(get_db),current_user: User = Depends(get_current_user)):
    users=db.query(User).all()
    res=[]
    for i in range(len(users)):
        dic={}
        dic["id"]=users[i].id
        dic["email"]=users[i].email
        dic["created_at"]=users[i].created_at
        res.append(dic)
    return res
        
def hash_password(password: str) -> str:
    return password_hash.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
def create_access_token(data:dict):
    to_encode=data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/auth/register")
def create_user(email: str, password: str, db: Session = Depends(get_db)):
    try:
        new_user = User(email=email, hashed_password=hash_password(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="This Email is already registered")

@app.post("/auth/login")
def login_check(email:str,password: str,db:Session=Depends(get_db)):
    check_for_email=db.query(User).filter(User.email == email).first()
    if check_for_email is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    hashed=check_for_email.hashed_password
    check_for_pass=verify_password(password,hashed)
    if check_for_pass:
        payload=str(check_for_email.id)
        return create_access_token({"sub":payload})        
    else:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
@app.post("/problems")
def create_problems(topic : str,title : str,difficulty : str = Query(..., description="Valid choices: Easy, Medium, Hard"),status : str = Query(..., description="Valid choices: Completed, Not Completed, Pending"),date_solved : date=Query(...,description="Format: YYYY-MM-DD"), current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    VALID_STATUSES=["Completed","Not Completed","Pending"]
    VALID_DIFFICULTIES=["Easy","Medium","Hard"]
    if not topic:
        raise HTTPException(status_code=400, detail="Topic should not be empty")
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid choices are: {VALID_STATUSES}")
    if difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty. Valid choices are: {VALID_DIFFICULTIES}")
    new_problem=Problem(user_id=current_user.id, topic=topic, title=title, difficulty=difficulty, status=status, date_solved=date_solved)
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    return {"id":new_problem.id,"title":new_problem.title}

@app.get("/problems")
def get_problem(current_user: User = Depends(get_current_user),db:Session=Depends(get_db),topic: str = None,status : str = Query(None, description="Valid choices: Completed, Not Completed, Pending")):
    query=db.query(Problem).filter(Problem.user_id==current_user.id)
    if topic:
        query=query.filter(Problem.topic==topic)
    if status:
        query=query.filter(Problem.status==status)
    records=query.all()
    return [rec_to_dic(p) for p in records]

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
        ans["Problems_solved"]=rec[1]
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

@app.put("/problems/{id}")
def update_problem(id : int,status:str = Query(None, description="Valid choices: Completed, Not Completed, Pending"),date_solved:date=Query(None,description="Format: YYYY-MM-DD"),current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    VALID_STATUSES=["Completed","Not Completed","Pending"]
    if status and (status not in VALID_STATUSES):
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid choices are: {VALID_STATUSES}")
    
    problem=db.query(Problem).filter(Problem.id==id,Problem.user_id==current_user.id).first()
    if problem:
        if status:
            problem.status=status
        if date_solved:
            problem.date_solved=date_solved
        db.commit()
        return rec_to_dic(problem)
    else:
        raise HTTPException(status_code=404, detail="Problem Not Found")

@app.delete("/problems/{id}")
def delete_problem(id : int,current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    problem=db.query(Problem).filter(Problem.id==id,Problem.user_id==current_user.id).first()
    if problem:
        id_val=problem.id
        db.delete(problem)
        db.commit()
        return f"The Record of id:{id_val} has been deleted"
    else:
        raise HTTPException(status_code=404, detail="Problem Not Found")

@app.post("/resources")
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

@app.post("/companies")
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

