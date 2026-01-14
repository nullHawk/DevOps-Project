"""CRUD operations for database models."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Task, User
from app.schemas import UserCreate, TaskCreate, TaskUpdate, TaskStatus
from app.security import get_password_hash


# User CRUD operations
def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> User | None:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


# Task CRUD operations
def create_task(db: Session, user_id: int, task: TaskCreate) -> Task:
    """Create a new task."""
    db_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int) -> Task | None:
    """Get task by ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_user_tasks(db: Session, user_id: int, status: TaskStatus | None = None) -> list[Task]:
    """Get all tasks for a user, optionally filtered by status."""
    query = db.query(Task).filter(Task.user_id == user_id)
    if status:
        query = query.filter(Task.status == status)
    return query.all()


def update_task(db: Session, task: Task, task_update: TaskUpdate) -> Task:
    """Update a task."""
    update_data = task_update.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
    elif "status" in update_data and update_data["status"] != TaskStatus.COMPLETED:
        update_data["completed_at"] = None

    for field, value in update_data.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    """Delete a task."""
    db.delete(task)
    db.commit()


def get_task_summary(db: Session, user_id: int) -> dict:
    """Get task summary for a user."""
    tasks = get_user_tasks(db, user_id)
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
    todo = sum(1 for t in tasks if t.status == TaskStatus.TODO)

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "in_progress_tasks": in_progress,
        "todo_tasks": todo,
        "completion_rate": (completed / total * 100) if total > 0 else 0,
    }
