from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Intern(Base):
    __tablename__ = "interns"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    cnic = Column(String, nullable=True)

    start_date = Column(Date, nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    valid_until = Column(Date, nullable=False)

    photo_path = Column(String, nullable=True)
    card_front_path = Column(String, nullable=True)
    card_back_path = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    attendance_logs = relationship("AttendanceLog", back_populates="intern")
class AttendanceLog(Base):
    """Placeholder for phase 2 (barcode scan in/out). Not wired up yet."""
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    intern_id = Column(Integer, ForeignKey("interns.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    direction = Column(String, nullable=False)  # "in" or "out"

    intern = relationship("Intern", back_populates="attendance_logs")
