# app/db/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True, index=True)
    height = Column(Float)
    weight = Column(Float)
    gender = Column(String)
    injury_history = Column(Text)
    fitness_goal = Column(Text)

    exercises = relationship("ExerciseLog", back_populates="user")
    journals = relationship("JournalEntry", back_populates="user")


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_type = Column(String)   # pushup, squat, cobra, etc.
    reps = Column(Integer)
    accuracy = Column(Float)
    state = Column(String)           # up, down, idle
    emotion = Column(String)         # happy, tired, neutral
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # ✅ New breathing fields
    breathing_bpm = Column(Float, nullable=True)
    breathing_irregular = Column(Boolean, default=False)

    user = relationship("User", back_populates="exercises")


class JournalEntry(Base):
    __tablename__ = "journals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    entry_text = Column(Text)
    injury_history = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="journals")