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
import math

from ..database import get_db
from ..models import Intern, Admin
from ..schemas import InternOut, InternVerifyOut, InternUpdate
from ..auth import get_current_admin
from ..id_generator import generate_unique_id
from ..date_utils import calculate_valid_until
from ..card_generator import generate_front_card, generate_back_card
from ..document_generator import (
    generate_security_letter,
    generate_offer_letter,
    generate_certificate,
)

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
    university: str = Form(...),
    discipline: str = Form(...),
    gender: str = Form(...),
    department: str = Form(...),
    cnic: str = Form(...),
    skills: str | None = Form(None),
    start_date: date = Form(...),
    end_date: date = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    name = name.strip()
    university = university.strip()
    discipline = discipline.strip()
    gender = gender.strip()
    department = department.strip()
    cnic = cnic.strip()
    skills = skills.strip() if skills else None

    if not name or not university or not discipline or not department or not cnic:
      raise HTTPException(
        status_code=400,
        detail="Name, university, discipline, department, and CNIC are required."
    )

    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="End date must be after the start date.")

    duration_weeks = math.ceil((end_date - start_date).days / 7)

    if not photo or not photo.filename:
        raise HTTPException(status_code=400, detail="A photo is required to generate the ID card.")

    if db.query(Intern).filter(Intern.cnic == cnic).first():
        raise HTTPException(status_code=400, detail="An intern with this CNIC already exists.")

    valid_until = end_date

    os.makedirs(PHOTO_DIR, exist_ok=True)
    ext = os.path.splitext(photo.filename)[1] or ".jpg"

    for _ in range(5):
        unique_id = generate_unique_id(db)
        photo_path = os.path.join(PHOTO_DIR, f"{unique_id}{ext}")

        # Rewind before every write attempt -- on a retry (IntegrityError
        # below) the underlying stream is already at EOF from the previous
        # copy, and skipping this would silently write a 0-byte photo file
        # while still letting the intern record get created successfully.
        photo.file.seek(0)
        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

        intern = Intern(
            unique_id=unique_id,

            name=name,
            gender=gender,
            skills=skills,

            university=university,
            discipline=discipline,
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


@router.get("/verify/{unique_id}", response_model=InternVerifyOut)
def verify_intern(unique_id: str, db: Session = Depends(get_db)):
    intern = db.query(Intern).filter(Intern.unique_id == unique_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Invalid intern ID")
    return intern


@router.get("/verify/{unique_id}/photo")
def verify_intern_photo(unique_id: str, db: Session = Depends(get_db)):
    intern = db.query(Intern).filter(Intern.unique_id == unique_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Invalid intern ID")

    if not intern.photo_path or not os.path.exists(intern.photo_path):
        raise HTTPException(status_code=404, detail="Photo not found")

    ext = os.path.splitext(intern.photo_path)[1].lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")

    return FileResponse(intern.photo_path, media_type=media_type)


@router.get("/{intern_id}", response_model=InternOut)
def get_intern(intern_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern


@router.patch("/{intern_id}", response_model=InternOut)
def update_intern(
    intern_id: int,
    payload: InternUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    for field in ("name", "gender", "university", "discipline", "department", "cnic", "skills"):
        if field in updates and updates[field] is not None:
            updates[field] = updates[field].strip()

    if "cnic" in updates and updates["cnic"] != intern.cnic:
        existing = (
            db.query(Intern)
            .filter(Intern.cnic == updates["cnic"], Intern.id != intern_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="An intern with this CNIC already exists.")

    # end_date isn't a real column on Intern -- it maps onto valid_until.
    # Pull it out before the generic setattr loop so we don't try to set
    # a non-existent attribute on the model.
    end_date = updates.pop("end_date", None)

    for field, value in updates.items():
        setattr(intern, field, value)

    # Recompute duration_weeks + valid_until together whenever either the
    # start or the end of the internship changes, exactly like create_intern
    # does -- valid_until is always the EXACT date picked, duration_weeks is
    # just a derived approximation for display/reporting.
    if "start_date" in updates or end_date is not None:
        new_end = end_date if end_date is not None else intern.valid_until

        if new_end <= intern.start_date:
            raise HTTPException(status_code=400, detail="End date must be after the start date.")

        intern.duration_weeks = math.ceil((new_end - intern.start_date).days / 7)
        intern.valid_until = new_end

    db.commit()
    db.refresh(intern)
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


def _pdf_response(buffer: io.BytesIO, filename: str):
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{intern_id}/card/pdf")
def download_card_pdf(intern_id: int, db: Session = Depends(get_db),
                       admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    if not intern.card_front_path or not intern.card_back_path or \
       not os.path.exists(intern.card_front_path) or not os.path.exists(intern.card_back_path):
        raise HTTPException(status_code=404, detail="Card not generated yet")

    front = Image.open(intern.card_front_path).convert("RGB")
    back = Image.open(intern.card_back_path).convert("RGB")

    buffer = io.BytesIO()
    front.save(buffer, format="PDF", save_all=True, append_images=[back], resolution=300.0)
    buffer.seek(0)

    filename = f"{intern.unique_id}.pdf"
    return _pdf_response(buffer, filename)


@router.get("/{intern_id}/security-letter/pdf")
def download_security_letter_pdf(intern_id: int, db: Session = Depends(get_db),
                                  admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    buffer = generate_security_letter(intern)
    filename = f"{intern.unique_id}_security_letter.pdf"
    return _pdf_response(buffer, filename)


@router.get("/{intern_id}/offer-letter/pdf")
def download_offer_letter_pdf(intern_id: int, db: Session = Depends(get_db),
                               admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    buffer = generate_offer_letter(intern)
    filename = f"{intern.unique_id}_offer_letter.pdf"
    return _pdf_response(buffer, filename)


@router.get("/{intern_id}/certificate/pdf")
def download_certificate_pdf(intern_id: int, db: Session = Depends(get_db),
                              admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    buffer = generate_certificate(intern)
    filename = f"{intern.unique_id}_certificate.pdf"
    return _pdf_response(buffer, filename)

