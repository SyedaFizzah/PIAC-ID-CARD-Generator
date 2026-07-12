"""
Run this once to create your admin login.
Usage: python create_admin.py
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, Base, engine
from app.models import Admin
from app.auth import hash_password

Base.metadata.create_all(bind=engine)

username = input("Admin username: ").strip()
password = input("Admin password: ").strip()
db = SessionLocal()
existing = db.query(Admin).filter(Admin.username == username).first()
if existing:
    print("That username already exists.")
else:
    admin = Admin(username=username, hashed_password=hash_password(password))
    db.add(admin)
    db.commit()
    print(f"Admin '{username}' created.")
db.close()
