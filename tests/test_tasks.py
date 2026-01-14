"""Tests for task endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.schemas import UserCreate


def create_test_user_and_get_token(client: TestClient, db: Session, user_data: dict) -> tuple[str, int]:
    """Helper to create user and get auth token."""
    # Create user
    user_create = UserCreate(**user_data)
    user = crud.create_user(db, user_create)

    # Login
    response = client.post(
        "/auth/login",
        params={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    token = response.json()["access_token"]
    return token, user.id


@pytest.fixture
def auth_token(client: TestClient, db: Session, test_user_data: dict):
    """Get authenticated token."""
    token, user_id = create_test_user_and_get_token(client, db, test_user_data)
    return {"Authorization": f"Bearer {token}"}


def test_create_task(
    client: TestClient, auth_token: dict, test_task_data: dict
):
    """Test creating a task."""
    response = client.post(
        "/tasks",
        json=test_task_data,
        headers=auth_token,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_task_data["title"]
    assert data["status"] == "todo"
    assert "id" in data


def test_create_task_unauthorized(client: TestClient, test_task_data: dict):
    """Test creating task without authentication."""
    response = client.post("/tasks", json=test_task_data)
    assert response.status_code == 403


def test_list_tasks_empty(client: TestClient, auth_token: dict):
    """Test listing empty tasks."""
    response = client.get("/tasks", headers=auth_token)
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks(
    client: TestClient, db: Session, auth_token: dict, test_user_data: dict, test_task_data: dict
):
    """Test listing tasks."""
    # Create tasks
    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    assert response.status_code == 201

    # List tasks
    response = client.get("/tasks", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == test_task_data["title"]


def test_list_tasks_by_status(
    client: TestClient, auth_token: dict, test_task_data: dict
):
    """Test filtering tasks by status."""
    # Create task
    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    assert response.status_code == 201

    # List todos
    response = client.get("/tasks?status=todo", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    # List completed
    response = client.get("/tasks?status=completed", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_task(
    client: TestClient, auth_token: dict, test_task_data: dict
):
    """Test getting a specific task."""
    # Create task
    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    task_id = response.json()["id"]

    # Get task
    response = client.get(f"/tasks/{task_id}", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == test_task_data["title"]


def test_get_nonexistent_task(client: TestClient, auth_token: dict):
    """Test getting nonexistent task."""
    response = client.get("/tasks/999", headers=auth_token)
    assert response.status_code == 404


def test_update_task(
    client: TestClient, auth_token: dict, test_task_data: dict
):
    """Test updating a task."""
    # Create task
    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    task_id = response.json()["id"]

    # Update task
    update_data = {
        "title": "Updated Task",
        "status": "in_progress",
    }
    response = client.put(
        f"/tasks/{task_id}",
        json=update_data,
        headers=auth_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["status"] == "in_progress"


def test_complete_task(
    client: TestClient, auth_token: dict, test_task_data: dict
):
    """Test marking task as completed."""
    # Create task
    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    task_id = response.json()["id"]

    # Mark as completed
    update_data = {"status": "completed"}
    response = client.put(
        f"/tasks/{task_id}",
        json=update_data,
        headers=auth_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_delete_task(
    client: TestClient, auth_token: dict, test_task_data: dict
):
    """Test deleting a task."""
    # Create task
    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    task_id = response.json()["id"]

    # Delete task
    response = client.delete(f"/tasks/{task_id}", headers=auth_token)
    assert response.status_code == 204

    # Verify deletion
    response = client.get(f"/tasks/{task_id}", headers=auth_token)
    assert response.status_code == 404


def test_delete_nonexistent_task(client: TestClient, auth_token: dict):
    """Test deleting nonexistent task."""
    response = client.delete("/tasks/999", headers=auth_token)
    assert response.status_code == 404


def test_task_summary(
    client: TestClient, auth_token: dict, test_task_data: dict
):
    """Test task summary endpoint."""
    # Create multiple tasks with different statuses
    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    task_id_1 = response.json()["id"]

    response = client.post("/tasks", json=test_task_data, headers=auth_token)
    assert response.status_code == 201

    # Mark one as completed
    client.put(
        f"/tasks/{task_id_1}",
        json={"status": "completed"},
        headers=auth_token,
    )

    # Get summary
    response = client.get("/tasks/summary/stats", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 1
    assert data["todo_tasks"] == 1
