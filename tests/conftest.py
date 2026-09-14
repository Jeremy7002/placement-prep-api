import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from alembic import command
from alembic.config import Config as AlembicConfig

from main import app
from database import Base, get_db
from settings import get_settings


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine using TEST database URL."""
    settings = get_settings()
    test_db_url = settings.database_url.replace(
        "placement_api", "placement_prep_test"
    )
    
    engine = create_engine(test_db_url)
    
    # Run Alembic migrations to create schema
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    command.upgrade(alembic_cfg, "head")
    
    yield engine
    
    # Cleanup: drop all tables after all tests finish
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_session(test_db_engine):
    """Create a fresh database session for each test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(test_db_session):
    """Create a TestClient that uses the test database."""
    def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()