"""Conftest for pytest fixtures."""

import os

# Set testing environment variables BEFORE any app imports
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app

# Use SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override get_db for tests."""
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    yield override_get_db().__next__()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create test client."""
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }


@pytest.fixture
def test_task_data():
    """Test task data."""
    return {
        "title": "Test Task",
        "description": "Test task description",
        "priority": "high",
        "status": "todo",
    }
