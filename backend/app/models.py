from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Intern(Base):
    __tablename__ = "interns"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String, unique=True, index=True, nullable=False)

    # Personal details
    name = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)

    # Education details
    university = Column(String, nullable=False)
    discipline = Column(String, nullable=False)
    department = Column(String, nullable=False)

    # Certificate-only fields, editable after creation
    project_description = Column(String, nullable=True)
    certificate_path = Column(String, nullable=True)

    # Sensitive information
    cnic = Column(String, nullable=False)
    cnic_front_path = Column(String, nullable=True)
    cnic_back_path = Column(String, nullable=True)

    # Optional commendable skills / achievements
    skills = Column(String, nullable=True)

    # Internship period
    start_date = Column(Date, nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    valid_until = Column(Date, nullable=False)

    # Files
    photo_path = Column(String, nullable=False)
    ID_card_front_path = Column(String, nullable=True)   # reverted to nullable — card is generated AFTER intern creation
    ID_card_back_path = Column(String, nullable=True)    # same
    university_id_card_front_path = Column(String, nullable=True)
    university_id_card_back_path = Column(String, nullable=True)
    CV_path = Column(String, nullable=True)               # optional, asked for at creation

    # Staff links — needed for card designation + both letters + certificate
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=True)
    supervisor_id = Column(Integer, ForeignKey("supervisors.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=True)
    mentor = relationship("Mentor")
    supervisor = relationship("Supervisor")
    manager = relationship("Manager")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    department = Column(String, nullable=False)

class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    department = Column(String, nullable=False)