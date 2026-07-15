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

'''
class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    intern_id = Column(Integer, ForeignKey("interns.id"), nullable=False)
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())

    intern = relationship("Intern", back_populates="attendance_logs")
'''

class Intern(Base):
    __tablename__ = "interns"

    id = Column(Integer, primary_key=True, index=True)

    # Public card ID
    unique_id = Column(String, unique=True, index=True, nullable=False)

    # Personal details
    name = Column(String, nullable=False)
    gender = Column(String, nullable=True)

    # Education details
    university = Column(String, nullable=True)
    discipline = Column(String, nullable=True)
    department = Column(String, nullable=True)

    # Sensitive information
    cnic = Column(String, nullable=True)

    # Optional commendable skills / achievements
    skills = Column(String, nullable=True)

    # Internship period
    start_date = Column(Date, nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    valid_until = Column(Date, nullable=False)

    # Files
    photo_path = Column(String, nullable=True)
    card_front_path = Column(String, nullable=True)
    card_back_path = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

'''
    attendance_logs = relationship(
        "AttendanceLog",
        back_populates="intern"
    )
'''