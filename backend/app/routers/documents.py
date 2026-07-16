from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Intern, Admin
from ..auth import get_current_admin
from ..document_generator import (
    generate_security_letter,
    generate_offer_letter,
    generate_certificate,
)
from ._responses import pdf_response

router = APIRouter(prefix="/interns", tags=["documents"])


def _get_intern_or_404(intern_id: int, db: Session) -> Intern:
    intern = db.query(Intern).filter(Intern.id == intern_id).first()
    if not intern:
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern


@router.get("/{intern_id}/security-letter/pdf")
def download_security_letter_pdf(intern_id: int, db: Session = Depends(get_db),
                                  admin: Admin = Depends(get_current_admin)):
    intern = _get_intern_or_404(intern_id, db)
    buffer = generate_security_letter(intern)
    return pdf_response(buffer, f"{intern.unique_id}_security_letter.pdf")


@router.get("/{intern_id}/offer-letter/pdf")
def download_offer_letter_pdf(intern_id: int, db: Session = Depends(get_db),
                               admin: Admin = Depends(get_current_admin)):
    intern = _get_intern_or_404(intern_id, db)
    buffer = generate_offer_letter(intern)
    return pdf_response(buffer, f"{intern.unique_id}_offer_letter.pdf")


@router.get("/{intern_id}/certificate/pdf")
def download_certificate_pdf(intern_id: int, db: Session = Depends(get_db),
                              admin: Admin = Depends(get_current_admin)):
    intern = _get_intern_or_404(intern_id, db)
    buffer = generate_certificate(intern)
    return pdf_response(buffer, f"{intern.unique_id}_certificate.pdf")
