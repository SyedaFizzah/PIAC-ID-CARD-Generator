"""
Generates unique intern IDs in the format: PIA + MM + YY + 001, 002, ...
e.g. an intern created in July 2026 -> PIA0726001, PIA0726002, ...
Sequence resets every month.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Intern


def generate_unique_id(db: Session) -> str:
    now = datetime.utcnow()
    mm = now.strftime("%m")
    yy = now.strftime("%y")
    prefix = f"PIA{mm}{yy}"

    # count existing interns created with this prefix this month
    count = (
        db.query(func.count(Intern.id))
        .filter(Intern.unique_id.like(f"{prefix}%"))
        .scalar()
    )
    seq = count + 1
    return f"{prefix}{seq:03d}"
