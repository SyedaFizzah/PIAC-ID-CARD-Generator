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
    father_name: Optional[str] = None
    gender: Optional[str] = None
    skills: Optional[str] = None

    university: Optional[str] = None
    discipline: Optional[str] = None
    department: Optional[str] = None

    cnic: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None  # maps onto Intern.valid_until — see update_intern


