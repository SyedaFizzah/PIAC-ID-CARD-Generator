import os
import math
import shutil
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models import Intern, Admin
from ..schemas import InternOut, InternVerifyOut, InternUpdate
from ..auth import get_current_admin
from ..id_generator import generate_unique_id
from ..paths import PHOTO_DIR

router = APIRouter(prefix="/interns", tags=["interns"])

_PHOTO_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


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
            detail="Name, university, discipline, department, and CNIC are required.",
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
    ext = os.path.splitext(photo.filename)[1] or ".jpg" or ".jpeg" or ".png" or ".webp"

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
    media_type = _PHOTO_MEDIA_TYPES.get(ext, "application/octet-stream")
    return FileResponse(intern.photo_path, media_type=media_type)


@router.get("/{intern_id}", response_model=InternOut)
def get_intern(intern_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern

@router.post("/{intern_id}/photo", response_model=InternOut)
def update_intern_photo(
    intern_id: int,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")

    if not photo or not photo.filename:
        raise HTTPException(status_code=400, detail="A photo file is required.")

    os.makedirs(PHOTO_DIR, exist_ok=True)
    ext = os.path.splitext(photo.filename)[1] or ".jpg"
    new_photo_path = os.path.join(PHOTO_DIR, f"{intern.unique_id}{ext}")

    photo.file.seek(0)
    with open(new_photo_path, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    # If the extension changed (e.g. old was .png, new upload is .jpg),
    # clean up the stale file so we don't accumulate orphans on disk.
    old_path = intern.photo_path
    if old_path and old_path != new_photo_path and os.path.exists(old_path):
        os.remove(old_path)

    intern.photo_path = new_photo_path
    db.commit()
    db.refresh(intern)
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




