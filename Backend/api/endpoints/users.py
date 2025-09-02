from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import SessionLocal
from app.schemas.user import UserCreate, UserResponse

# 👇 define router first
router = APIRouter(prefix="/users", tags=["Users"])

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        name=user.name,
        age=user.age,
        email=user.email,
        height=user.height,
        weight=user.weight,
        gender=user.gender,
        injury_history=user.injury_history,
        fitness_goal=user.fitness_goal
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.id == user_id).first()
