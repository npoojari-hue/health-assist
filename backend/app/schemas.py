# schemas.py - request bodies. Every field is optional and range-checked.
from typing import Optional
from pydantic import BaseModel, Field


class Profile(BaseModel):
    age: Optional[int] = Field(None, ge=18, le=110)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    active_minutes_week: Optional[int] = Field(None, ge=0, le=3000)
    strength_days_week: Optional[int] = Field(None, ge=0, le=7)
    sitting_hours_day: Optional[float] = Field(None, ge=0, le=24)
    screen_hours_day: Optional[float] = Field(None, ge=0, le=24)


class Question(BaseModel):
    text: str = Field(..., min_length=3, max_length=500)
    model: Optional[str] = None


class Feedback(BaseModel):
    history_id: int
    rating: int = Field(..., ge=1, le=5)
