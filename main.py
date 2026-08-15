import logging
from fastapi import FastAPI
from database import Base, engine
from middleware import RequestIDMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.problems import router as problems_router
from routers.resources import router as resources_router
from routers.companies import router as companies_router
from routers.analytics import router as analytics_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(RequestIDMiddleware)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(problems_router)
app.include_router(resources_router)
app.include_router(companies_router)
app.include_router(analytics_router)