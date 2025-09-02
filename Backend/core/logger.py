# app/core/logger.py
from app.db.database import SessionLocal
from app.db import models

def log_event(user_id: int, data: dict):
    """
    Logs workout + breathing + emotion into ExerciseLog table.
    """
    db = SessionLocal()
    try:
        exercise = models.ExerciseLog(
            user_id=user_id,
            exercise_type=data.get("exercise"),
            reps=data.get("rep_count", 0),
            accuracy=data.get("accuracy", 0.0),
            state=data.get("state", "idle"),
            emotion=data.get("emotion", "neutral"),
            confidence=data.get("confidence", 0.0),
            breathing_bpm=data.get("breathing_bpm"),
            breathing_irregular=data.get("breathing_irregular"),
            timestamp=data.get("timestamp"),
        )
        db.add(exercise)
        db.commit()
    except Exception as e:
        print(f"⚠️ Error logging event: {e}")
    finally:
        db.close()
