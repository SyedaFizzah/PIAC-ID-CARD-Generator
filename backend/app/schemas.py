from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class AdminLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class InternCreate(BaseModel):
    name: str
    department: str
    cnic: str
    start_date: date
    duration_weeks: int


class InternOut(BaseModel):
    id: int
    unique_id: str
    name: str
    department: str
    cnic: str
    photo_path: str
    start_date: date
    duration_weeks: int
    valid_until: date
    card_front_path: Optional[str]
    card_back_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True