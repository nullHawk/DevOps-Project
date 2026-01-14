"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.schemas import UserCreate


def test_register_user(client: TestClient, test_user_data: dict):
    """Test user registration."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data


def test_register_duplicate_username(client: TestClient, test_user_data: dict, db: Session):
    """Test registering duplicate username."""
    # Create first user
    user_create = UserCreate(**test_user_data)
    crud.create_user(db, user_create)

    # Try to create duplicate
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_register_duplicate_email(client: TestClient, test_user_data: dict, db: Session):
    """Test registering duplicate email."""
    # Create first user
    user_create = UserCreate(**test_user_data)
    crud.create_user(db, user_create)

    # Try to create user with same email but different username
    duplicate_data = test_user_data.copy()
    duplicate_data["username"] = "differentuser"
    response = client.post("/auth/register", json=duplicate_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_login_success(client: TestClient, test_user_data: dict, db: Session):
    """Test successful login."""
    # Create user
    user_create = UserCreate(**test_user_data)
    crud.create_user(db, user_create)

    # Login
    response = client.post(
        "/auth/login",
        params={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, test_user_data: dict, db: Session):
    """Test login with invalid credentials."""
    # Create user
    user_create = UserCreate(**test_user_data)
    crud.create_user(db, user_create)

    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        params={
            "username": test_user_data["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user."""
    response = client.post(
        "/auth/login",
        params={
            "username": "nonexistent",
            "password": "password",
        },
    )
    assert response.status_code == 401
