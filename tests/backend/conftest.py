import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.db.seed import seed_database
from app.main import app
from app.models.domain import User, EmployeeProfile

# In-memory SQLite engine for rapid unit tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        seed_database(db=db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(db_session):
    admin = db_session.query(User).filter(User.role == "admin").first()
    return create_access_token(admin.email)


@pytest.fixture
def hr_token(db_session):
    hr = db_session.query(User).filter(User.role == "hr").first()
    return create_access_token(hr.email)


@pytest.fixture
def employee_token_and_profile(db_session):
    emp_user = db_session.query(User).filter(User.role == "employee").first()
    profile = db_session.query(EmployeeProfile).filter(EmployeeProfile.user_id == emp_user.id).first()
    token = create_access_token(emp_user.email)
    return token, profile, emp_user


@pytest.fixture
def second_employee_token_and_profile(db_session):
    emp_users = db_session.query(User).filter(User.role == "employee").all()
    second_user = emp_users[1] if len(emp_users) > 1 else emp_users[0]
    profile = db_session.query(EmployeeProfile).filter(EmployeeProfile.user_id == second_user.id).first()
    token = create_access_token(second_user.email)
    return token, profile, second_user
