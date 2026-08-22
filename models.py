from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Date
from sqlalchemy.sql import func
from database import Base

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
    difficulty_notes = Column(String(500), nullable=True)
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
