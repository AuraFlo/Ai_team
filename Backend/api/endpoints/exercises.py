from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/exercises", tags=["Exercises"])

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/log")
def log_exercise(
    user_id: int,
    exercise_type: str,
    reps: int,
    accuracy: float,
    state: Optional[str] = None,
    emotion: Optional[str] = None,
    confidence: Optional[float] = None,
    breathing_bpm: Optional[float] = None,
    breathing_irregular: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    General endpoint for logging any exercise (pushups, squats, lunges, etc.)
    """

    try:
        exercise = models.ExerciseLog(
            user_id=user_id,
            exercise_type=exercise_type,
            reps=reps,
            accuracy=accuracy,
            state=state or "idle",
            emotion=emotion or "neutral",
            confidence=confidence or 0.0,
            breathing_bpm=breathing_bpm,
            breathing_irregular=breathing_irregular,
            timestamp=datetime.utcnow()
        )

        db.add(exercise)
        db.commit()
        db.refresh(exercise)

        return {
            "message": f"{exercise_type} logged successfully",
            "exercise_id": exercise.id,
            "user_id": user_id,
            "reps": reps,
            "accuracy": accuracy,
            "state": exercise.state,
            "emotion": exercise.emotion,
            "confidence": exercise.confidence,
            "breathing_bpm": exercise.breathing_bpm,
            "breathing_irregular": exercise.breathing_irregular,
            "timestamp": exercise.timestamp
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
