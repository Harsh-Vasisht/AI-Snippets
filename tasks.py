
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: str = None
    owner_id: int

@router.post("/tasks/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == task.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Owner not found")
    db_task = Task(title=task.title, description=task.description, owner_id=task.owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks/")
def list_tasks(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        return db.query(Task).all()
    return db.query(Task).filter(Task.owner_id == user_id).all()
