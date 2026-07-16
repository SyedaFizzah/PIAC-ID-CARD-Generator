import os
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from PIL import Image

from ..database import get_db
from ..models import Intern, Admin
from ..auth import get_current_admin
from ..card_generator import generate_front_card, generate_back_card
from ..paths import CARD_DIR
from ._responses import pdf_response

router = APIRouter(prefix="/interns", tags=["cards"])


def _get_intern_or_404(intern_id: int, db: Session) -> Intern:
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern


@router.post("/{intern_id}/generate-card")
def generate_card(intern_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    intern = _get_intern_or_404(intern_id, db)

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
    intern = _get_intern_or_404(intern_id, db)

    path = intern.card_front_path if side == "front" else intern.card_back_path
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Card not generated yet")

    return FileResponse(path, media_type="image/png", filename=f"{intern.unique_id}_{side}.png")


@router.get("/{intern_id}/card/pdf")
def download_card_pdf(intern_id: int, db: Session = Depends(get_db),
                       admin: Admin = Depends(get_current_admin)):
    intern = _get_intern_or_404(intern_id, db)

    if not intern.card_front_path or not intern.card_back_path or \
       not os.path.exists(intern.card_front_path) or not os.path.exists(intern.card_back_path):
        raise HTTPException(status_code=404, detail="Card not generated yet")

    front = Image.open(intern.card_front_path).convert("RGB")
    back = Image.open(intern.card_back_path).convert("RGB")

    buffer = io.BytesIO()
    front.save(buffer, format="PDF", save_all=True, append_images=[back], resolution=300.0)
    buffer.seek(0)

    return pdf_response(buffer, f"{intern.unique_id}.pdf")
