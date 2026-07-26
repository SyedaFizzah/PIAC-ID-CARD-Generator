import os
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Intern, Admin
from ..auth import get_current_admin
from ..security_letter_generator import generate_security_letter, MAX_CANDIDATES
from ..paths import SECURITY_LETTER_DIR

router = APIRouter(prefix="/security-letters", tags=["security-letters"])


class SecurityLetterRequest(BaseModel):
    intern_ids: List[int] = Field(..., min_items=1, max_items=MAX_CANDIDATES)
    start_date: date
    end_date: date


@router.post("/generate")
def generate_security_letter_route(
    req: SecurityLetterRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    interns = db.query(Intern).filter(Intern.id.in_(req.intern_ids)).all()

    found_ids = {i.id for i in interns}
    if missing := set(req.intern_ids) - found_ids:
        raise HTTPException(status_code=404, detail=f"Intern ids not found: {sorted(missing)}")

    departments = {i.department for i in interns}
    if len(departments) > 1:
        raise HTTPException(
            status_code=400,
            detail=f"Selected interns span multiple departments ({', '.join(sorted(departments))}). "
                   "Generate one letter per department.",
        )
    department = departments.pop()

    try:
        pdf_path = generate_security_letter(
            interns=interns,
            department=department,
            start_date=req.start_date,
            end_date=req.end_date,
            output_dir=SECURITY_LETTER_DIR,
            session=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))