import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Intern, Admin
from ..auth import get_current_admin
from ..certificate_generator import generate_certificate
from ..paths import CERT_DIR  # add CERT_DIR = os.path.join(DATA_DIR, "certificates") to paths.py

router = APIRouter(prefix="/interns", tags=["certificates"])


def _get_intern_or_404(intern_id: int, db: Session) -> Intern:
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern


@router.post("/{intern_id}/generate-certificate")
def generate_certificate_route(intern_id: int, db: Session = Depends(get_db),
                                admin: Admin = Depends(get_current_admin)):
    intern = _get_intern_or_404(intern_id, db)

    out_dir = os.path.join(CERT_DIR, intern.unique_id)
    try:
        pdf_path = generate_certificate(intern, out_dir)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    intern.certificate_path = pdf_path
    db.commit()

    return {"unique_id": intern.unique_id, "certificate_path": pdf_path}


@router.get("/{intern_id}/certificate")
def download_certificate(intern_id: int, db: Session = Depends(get_db),
                          admin: Admin = Depends(get_current_admin)):
    intern = _get_intern_or_404(intern_id, db)

    if not intern.certificate_path or not os.path.exists(intern.certificate_path):
        raise HTTPException(status_code=404, detail="Certificate not generated yet")

    return FileResponse(intern.certificate_path, media_type="application/pdf",
                         filename=f"{intern.unique_id}_certificate.pdf")
