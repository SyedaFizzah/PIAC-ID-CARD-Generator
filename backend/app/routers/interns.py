import os
import re
import io
import shutil
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from PIL import Image

from ..database import get_db
from ..models import Intern, Admin
from ..schemas import InternOut
from ..auth import get_current_admin
from ..id_generator import generate_unique_id
from ..date_utils import calculate_valid_until
from ..card_generator import generate_front_card, generate_back_card

router = APIRouter(prefix="/interns", tags=["interns"])

PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "photos")
CARD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "cards")


def _safe_filename(name: str) -> str:
    """Strip characters that are illegal in filenames on Windows/macOS/Linux."""
    cleaned = re.sub(r'[\\/:*?"<>|]+', "", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "intern"


@router.post("", response_model=InternOut)
def create_intern(
    name: str = Form(...),
    department: str = Form(...),
    cnic: str = Form(...),
    start_date: date = Form(...),
    duration_weeks: int = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    name = name.strip()
    department = department.strip()
    cnic = cnic.strip()

    if not name or not department or not cnic:
        raise HTTPException(status_code=400, detail="Name, department, and CNIC are all required.")

    if duration_weeks <= 0:
        raise HTTPException(status_code=400, detail="Duration must be at least 1 week.")

    if not photo or not photo.filename:
        raise HTTPException(status_code=400, detail="A photo is required to generate the ID card.")

    if db.query(Intern).filter(Intern.cnic == cnic).first():
        raise HTTPException(status_code=400, detail="An intern with this CNIC already exists.")

    valid_until = calculate_valid_until(start_date, duration_weeks)

    # save photo first so we can store its path on the row
    os.makedirs(PHOTO_DIR, exist_ok=True)
    ext = os.path.splitext(photo.filename)[1] or ".jpg"

    # retry loop guards against a rare race on the monthly sequence
    for _ in range(5):
        unique_id = generate_unique_id(db)
        photo_path = os.path.join(PHOTO_DIR, f"{unique_id}{ext}")
        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

        intern = Intern(
            unique_id=unique_id,
            name=name,
            department=department,
            cnic=cnic,
            photo_path=photo_path,
            start_date=start_date,
            duration_weeks=duration_weeks,
            valid_until=valid_until,
        )
        db.add(intern)
        try:
            db.commit()
            db.refresh(intern)
            return intern
        except IntegrityError:
            db.rollback()
            os.remove(photo_path)

    raise HTTPException(status_code=500, detail="Could not allocate a unique intern ID, try again")


@router.get("", response_model=list[InternOut])
def list_interns(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    return db.query(Intern).order_by(Intern.created_at.desc()).all()


@router.get("/{intern_id}", response_model=InternOut)
def get_intern(intern_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern


@router.post("/{intern_id}/generate-card")
def generate_card(intern_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    front_path = os.path.join(CARD_DIR, f"{intern.unique_id}_front.png")
    back_path = os.path.join(CARD_DIR, f"{intern.unique_id}_back.png")

    generate_front_card(intern.name, intern.unique_id, intern.department, intern.photo_path, front_path)
    generate_back_card(intern.unique_id, intern.start_date, intern.valid_until, back_path)

    intern.card_front_path = front_path
    intern.card_back_path = back_path
    db.commit()

    return {"unique_id": intern.unique_id, "card_front_path": front_path, "card_back_path": back_path}


@router.get("/{intern_id}/card")
def download_card(intern_id: int, side: str = "front", db: Session = Depends(get_db),
                   admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    path = intern.card_front_path if side == "front" else intern.card_back_path
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Card not generated yet")

    return FileResponse(path, media_type="image/png", filename=f"{intern.unique_id}_{side}.png")


@router.get("/{intern_id}/card/pdf")
def download_card_pdf(intern_id: int, db: Session = Depends(get_db),
                       admin: Admin = Depends(get_current_admin)):
    """Front + back combined into one print-ready 2-page PDF, named after
    the intern (e.g. "Fizzah Masroor.pdf") so it's ready to hand straight
    to a print shop or a duplex printer."""
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    if not intern.card_front_path or not intern.card_back_path or \
       not os.path.exists(intern.card_front_path) or not os.path.exists(intern.card_back_path):
        raise HTTPException(status_code=404, detail="Card not generated yet")

    front = Image.open(intern.card_front_path).convert("RGB")
    back = Image.open(intern.card_back_path).convert("RGB")

    # resolution=300 makes each PDF page exactly the printed card size
    # (image pixels / 300 dpi), so it prints true-to-size on any printer
    # or can be sent straight to a card print shop without extra scaling.
    buffer = io.BytesIO()
    front.save(buffer, format="PDF", save_all=True, append_images=[back], resolution=300.0)
    buffer.seek(0)

    filename = f"{_safe_filename(intern.name)}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )