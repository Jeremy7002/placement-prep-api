from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import get_settings

db_settings = get_settings()
DATABASE_URL = db_settings.database_url

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set. Check your .env file or Render environment variables.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()