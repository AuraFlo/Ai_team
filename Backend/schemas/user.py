from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    age: Optional[int] = None
    email: str
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    injury_history: Optional[str] = None
    fitness_goal: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]
    email: str
    height: Optional[float]
    weight: Optional[float]
    gender: Optional[str]
    injury_history: Optional[str]
    fitness_goal: Optional[str]

    class Config:
        orm_mode = True
