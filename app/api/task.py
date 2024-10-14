# app/api/task.py
from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, Task
from app.db.db import get_db
from app.core.auth import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/tasks/", response_model=Task)
@limiter.limit("100/minute")  # Ограничение на 100 запросов в минуту
def create_task(
    request: Request,  # Добавьте request
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_task = Task(title=task.title, description=task.description, owner_id=user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks/", response_model=list[Task])
@limiter.limit("100/minute")  # Ограничение на 100 запросов в минуту
def read_tasks(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Task).filter(Task.owner_id == user.id).all()

@router.get("/tasks/{task_id}", response_model=Task)
@limiter.limit("100/minute")  # Ограничение на 100 запросов в минуту
def read_task(
    request: Request,  # Добавьте request
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=Task)
@limiter.limit("100/minute")  # Ограничение на 100 запросов в минуту
def update_task(
    request: Request,  
    task_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}")
def delete_task(
    request: Request,  
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}
