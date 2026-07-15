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
    gender: str
    university: str
    discipline: str
    department: str
    cnic: str
    skills: Optional[str] = None
    start_date: date
    end_date: date


class InternUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    skills: Optional[str] = None

    university: Optional[str] = None
    discipline: Optional[str] = None
    department: Optional[str] = None

    cnic: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None  # maps onto Intern.valid_until — see update_intern


class InternOut(BaseModel):

    id: int
    unique_id: str

    name: str
    gender: str | None

    university: str | None
    discipline: str | None
    department: str | None
    skills: str | None

    cnic: str | None

    start_date: date
    duration_weeks: int
    valid_until: date

    photo_path: str | None

    card_front_path: str | None
    card_back_path: str | None

    created_at: datetime


    class Config:
        from_attributes = True


class InternVerifyOut(BaseModel):
    """Public-facing subset — excludes cnic since this is returned to anyone scanning a card.
       Keeps photo_path so the verifier can display the photo alongside the details."""

    unique_id: str

    name: str
    gender: str | None
    university: str | None
    discipline: str | None
    department: str | None
    skills: str | None

    start_date: date
    duration_weeks: int
    valid_until: date

    photo_path: str | None


    class Config:
        from_attributes = True