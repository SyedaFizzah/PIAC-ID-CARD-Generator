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

    # Public card ID
    unique_id = Column(String, unique=True, index=True, nullable=False)

    # Personal details
    name = Column(String, nullable=False)
    father_name = Column(String, nullable=True)
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
    ID_card_front_path = Column(String, nullable=True)
    ID_card_back_path = Column(String, nullable=True)
    CV_path = Column(String, nullable=True)

class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    department = Column(String, nullable=False)

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