"""FastAPI application factory and main entrypoint."""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import __version__, crud
from app.config import settings
from app.database import Base, engine, get_db
from app.schemas import (
    HealthResponse,
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskSummary,
    TaskUpdate,
    Token,
    TokenData,
    UserCreate,
    UserResponse,
    VersionResponse,
)
from app.security import create_access_token, get_current_user, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create database tables on startup."""
    # Skip table creation during testing (tests handle their own setup)
    if os.environ.get("TESTING") != "1":
        Base.metadata.create_all(bind=engine)
    yield


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Advanced DevOps CI/CD for a Containerized Python Service - To-Do API",
    version=__version__,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Health and Version endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow())


@app.get("/version", response_model=VersionResponse, tags=["Health"])
async def version():
    """Version endpoint."""
    return VersionResponse(
        version=__version__,
        app_name=settings.app_name,
        timestamp=datetime.utcnow(),
    )


# Authentication endpoints
@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return crud.create_user(db, user)


@app.post("/auth/login", response_model=Token, tags=["Auth"])
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Task endpoints
@app.post(
    "/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"]
)
async def create_task(
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new task."""
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return crud.create_task(db, user.id, task)


@app.get("/tasks", response_model=list[TaskResponse], tags=["Tasks"])
async def list_tasks(
    status: TaskStatus | None = Query(None, description="Filter by task status"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all tasks for the current user."""
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return crud.get_user_tasks(db, user.id, status)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Verify ownership
    user = crud.get_user_by_username(db, current_user.username)
    if task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Verify ownership
    user = crud.get_user_by_username(db, current_user.username)
    if task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return crud.update_task(db, task, task_update)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a task."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Verify ownership
    user = crud.get_user_by_username(db, current_user.username)
    if task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    crud.delete_task(db, task)
    return None


@app.get("/tasks/summary/stats", response_model=TaskSummary, tags=["Tasks"])
async def get_task_summary(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get task summary and statistics."""
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    summary = crud.get_task_summary(db, user.id)
    return TaskSummary(**summary)


# User endpoints
@app.get("/users/me", response_model=UserResponse, tags=["Users"])
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user information."""
    user = crud.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
