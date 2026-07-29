"""
Renders one intern ID card from the real branded template
(templates/card_template.docx — a 2-page docx: page 1 = front, page 2 = back),
then converts it to a final PDF sheet:
  - front + back card images side by side at the top
  - a dashed separator
  - a Terms & Conditions section below

Windows-friendly pipeline (assumes Microsoft Word is installed):
  docxtpl        -> fills the template's Jinja placeholders
  docx2pdf       -> converts docx to PDF via MS Word COM automation
  PyMuPDF (fitz) -> rasterizes each PDF page to PNG (no Poppler needed)
  reportlab      -> composes the final sheet

Usage: python generate_card.py
"""

import shutil
from pathlib import Path

import fitz  # PyMuPDF
import qrcode
from docx2pdf import convert as docx2pdf_convert
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image, ImageDraw

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas

# generate_card.py lives in backend/app/, but the template, assets, and
# build folders live in backend/templates/card/ — point there explicitly
# rather than assuming they sit next to this script.
HERE = Path(__file__).parent
CARD_DIR = HERE.parent / "templates" / "card"
TEMPLATE_PATH = CARD_DIR / "card_template.docx"
ASSETS_DIR = CARD_DIR / "assets"

TERMS_HEADING = "TERMS & CONDITIONS"
TERMS_BODY = (
    "<b>Identification:</b> Interns must carry their ID card at all times "
    "within company premises for security and verification.<br/><br/>"
    "<b>Usage:</b> The ID card is company property, strictly personal, and "
    "must not be shared, duplicated, or used for unauthorized purposes."
)

# Actual card page size from the template (2.125in x 3.303in)
CARD_W = 2.125 * inch
CARD_H = 3.303 * inch
GAP = 2.0 * inch


def _ensure_sample_assets() -> tuple[Path, Path]:
    """Create sample photo/QR under assets/ if they are missing (for local testing)."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    photo_path = ASSETS_DIR / "sample_photo.jpeg"
    qr_path = ASSETS_DIR / "sample_qr.png"

    if not photo_path.exists():
        img = Image.new("RGB", (300, 380), "#d9d9d9")
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 280, 360], outline="#666666", width=3)
        draw.text((95, 180), "PHOTO", fill="#666666")
        img.save(photo_path)

    if not qr_path.exists():
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data("PIA-INT-0142")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="transparent").convert("RGBA")
        qr_img.save(qr_path)  # PNG supports alpha; keeps transparency

    return photo_path, qr_path


# ---------- Stage 1: fill the real template ----------

def render_card_docx(intern: dict, out_dir: Path) -> Path:
    """
    intern needs: name, unique_id, father_name, cnic, department,
                  start_date, valid_until, photo_path, qr_path
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Card template not found: {TEMPLATE_PATH}")

    out_dir.mkdir(parents=True, exist_ok=True)
    doc = DocxTemplate(str(TEMPLATE_PATH))

    photo = InlineImage(doc, intern["photo_path"], width=Mm(22), height=Mm(28))
    qr = InlineImage(doc, intern["qr_path"], width=Mm(18), height=Mm(18))

    ctx = {
        "name": intern["name"],
        "unique_id": intern["unique_id"],
        "father_name": intern["father_name"],
        "cnic": intern["cnic"],
        "department": intern["department"],
        "start_date": intern["start_date"],
        "valid_until": intern["valid_until"],
        "photo": photo,
        "qr_code": qr,
    }

    doc.render(ctx)
    out_path = out_dir / f"{intern['unique_id']}_card.docx"
    doc.save(str(out_path))
    return out_path


def convert_docx_to_pdf(docx_path: Path, out_dir: Path) -> Path:
    """Convert the rendered docx (2 pages: front, back) to PDF via MS Word."""
    pdf_path = out_dir / f"{docx_path.stem}.pdf"
    docx2pdf_convert(str(docx_path), str(pdf_path))
    if not pdf_path.exists():
        raise RuntimeError(f"docx2pdf did not produce {pdf_path}")
    return pdf_path


def pdf_pages_to_png(pdf_path: Path, out_dir: Path, dpi: int = 300) -> list[Path]:
    """Rasterize every page of the card PDF to PNG using PyMuPDF (no Poppler)."""
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pngs = []
    with fitz.open(str(pdf_path)) as doc:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix)
            png_path = out_dir / f"{pdf_path.stem}_p{i + 1}.png"
            pix.save(str(png_path))
            pngs.append(png_path)
    return pngs


# ---------- Stage 2: build the final sheet ----------

def build_final_sheet(front_png: Path, back_png: Path, out_path: Path) -> Path:
    """
    Places front + back card images side by side at the top of an A4 page,
    a dashed separator, then Terms & Conditions below.
    """
    page_w, page_h = A4
    c = canvas.Canvas(str(out_path), pagesize=A4)

    top_margin = 0.4 * inch
    side_margin = 1 * inch

    total_w = CARD_W * 2 + GAP
    start_x = (page_w - total_w) / 2
    y = page_h - top_margin - CARD_H

    c.drawImage(ImageReader(str(front_png)), start_x, y, width=CARD_W, height=CARD_H)
    c.drawImage(ImageReader(str(back_png)), start_x + CARD_W + GAP, y, width=CARD_W, height=CARD_H)

    # Dashed divider between front/back
    c.setDash(3, 2)
    c.line(start_x + CARD_W + GAP / 2, y, start_x + CARD_W + GAP / 2, y + CARD_H)
    c.setDash()

    # Full-width dashed separator below the card section
    separator_y = y - 0.3 * inch
    c.setDash(4, 3)
    c.setLineWidth(0.75)
    c.line(0.3 * inch, separator_y, page_w - 0.3 * inch, separator_y)
    c.setDash()

    # Terms & Conditions heading
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.8, 0, 0)
    heading_y = separator_y - 0.5 * inch
    c.drawString(side_margin, heading_y, TERMS_HEADING)
    c.setFillColorRGB(0, 0, 0)

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "terms_body", parent=styles["Normal"], fontSize=10, leading=14,
    )
    para = Paragraph(TERMS_BODY, body_style)
    text_w = page_w - 2 * side_margin
    _, text_h = para.wrap(text_w, page_h)
    para.drawOn(c, side_margin, heading_y - 0.35 * inch - text_h)

    c.save()
    return out_path


# ---------- Full pipeline ----------

def render_card(intern: dict, out_dir: Path) -> Path:
    docx_path = render_card_docx(intern, out_dir)
    card_pdf = convert_docx_to_pdf(docx_path, out_dir)
    pngs = pdf_pages_to_png(card_pdf, out_dir)
    if len(pngs) < 2:
        raise RuntimeError(
            f"Expected 2 pages (front, back) in {card_pdf.name}, got {len(pngs)}"
        )
    front_png, back_png = pngs[0], pngs[1]

    final_pdf = out_dir / f"{intern['unique_id']}.pdf"
    build_final_sheet(front_png, back_png, final_pdf)

    # clean up intermediates — only the composed sheet is the deliverable
    docx_path.unlink(missing_ok=True)
    card_pdf.unlink(missing_ok=True)
    for p in pngs:
        p.unlink(missing_ok=True)

    return final_pdf


if __name__ == "__main__":
    out = CARD_DIR / "build"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    photo_path, qr_path = _ensure_sample_assets()

    sample = {
        "name": "Syeda Fizzah Masroor",
        "unique_id": "PIA-INT-0142",
        "father_name": "Masroor Ahmed",
        "cnic": "42101-1234567-1",
        "department": "ERP Section",
        "start_date": "09-04-2026",
        "valid_until": "09-04-2027",
        "photo_path": str(photo_path),
        "qr_path": str(qr_path),
    }

    final_pdf = render_card(sample, out)
    print(f"Built: {final_pdf}")