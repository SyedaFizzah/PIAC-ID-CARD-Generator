import os
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from app.database import SessionLocal
from app.models import Intern, Admin, Supervisor
from ..auth import get_current_admin
from ..security_letter_generator import generate_security_letter, MAX_CANDIDATES
from ..paths import SECURITY_LETTER_DIR  # add to paths.py, same pattern as CARD_DIR

router = APIRouter(prefix="/security-letters", tags=["security-letters"])


class SecurityLetterRequest(BaseModel):
    intern_ids: List[int] = Field(..., min_items=0, max_items=MAX_CANDIDATES)
    supervisor_name: str
    section_name: str = None
    supervisor_designation: str
    supervisor_department: str

@router.post("/generate")
def generate_security_letter_route(req: SecurityLetterRequest, db: Session = Depends(get_db),
                                    admin: Admin = Depends(get_current_admin)):
    interns = db.query(Intern).filter(Intern.id.in_(req.intern_ids)).all()

    found_ids = {i.id for i in interns}
    missing = set(req.intern_ids) - found_ids
    if missing:
        raise HTTPException(status_code=404, detail=f"Intern ids not found: {sorted(missing)}")

    try:
        # collect departments from the selected interns (do not assume they are the same)
        departments = sorted({i.department for i in interns if getattr(i, 'department', None)})
        # if no explicit section_name provided, use department(s) as the section name
        section_name = req.section_name if req.section_name else (", ".join(departments) if departments else None)

        pdf_path = generate_security_letter(
            interns=interns,
            section_name=section_name,
            supervisor_name=req.supervisor_name,
            supervisor_designation=req.supervisor_designation,
            supervisor_department=req.supervisor_department,
            output_dir=SECURITY_LETTER_DIR,
        )
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(pdf_path, media_type="application/pdf",
                         filename=os.path.basename(pdf_path))
