"""
PIA Intern ID Card Generator

Front: loads Fizzah's Canva export as the base, overlays photo, name,
ID number, department, and a QR code (encodes the intern verification
URL for attendance scanning / public verification).

Back: T&C + expiry + a repeated QR code, positioned identically to the
front QR so both sides line up when the card is flipped.
"""
from dotenv import load_dotenv
load_dotenv()

from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode
import os
from datetime import date

PIA_GREEN = "#0A5C36"
PIA_GOLD = "#A6873C"
PIA_CREAM = "#F5F0E6"

BASE_DIR = os.path.dirname(__file__)
FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts")

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
FRONT_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "ID Card Template Front.png")
BACK_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "ID Card Template Back.png")

# Base URL the QR codes point at. Override via env var per environment
# (local/staging/prod) so cards printed in one environment don't point
# verifiers at the wrong server. Point this at your PUBLIC verify page,
# not the raw API, once that page exists.
VERIFY_BASE_URL = os.environ.get("VERIFY_BASE_URL", "http://localhost:5173/verify")

# --- Front layout: single vertical stack, all centered ---
PHOTO_BOX = (215, 260, 375, 490)
NAME_POS = (295, 545)
HEADING_POS = (295, 585)
ID_LABEL_POS = (295, 622)
DEPT_LABEL_POS = (295, 655)
QR_BOX = (210, 705, 380, 875)

# --- Back layout ---
BACK_ISSUE_POS = (295, 645)
BACK_VALID_POS = (295, 680)
BACK_QR_BOX = (210, 705, 380, 875)
BACK_CAPTION_POS = (295, 890)


def _verify_url(unique_id: str) -> str:
    return f"{VERIFY_BASE_URL}/{unique_id}"


def _font(name, size):
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if "Bold" in name \
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(fallback, size)


def _fit_font(draw, text, font_name, max_size, max_width, min_size=12):
    size = max_size
    while size > min_size:
        font = _font(font_name, size)
        width = draw.textbbox((0, 0), text, font=font)[2]
        if width <= max_width:
            return font
        size -= 1
    return _font(font_name, min_size)


def _draw_photo_placeholder(draw, box):
    draw.rounded_rectangle(box, radius=16, fill="#E8E8E8", outline=PIA_GREEN, width=4)


def _paste_photo(card, photo_path, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    photo = Image.open(photo_path).convert("RGB")
    photo = ImageOps.fit(photo, (w, h), method=Image.LANCZOS)

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=16, fill=255)

    card.paste(photo, (x0, y0), mask)
    ImageDraw.Draw(card).rounded_rectangle(box, radius=16, outline=PIA_GREEN, width=3)


def _make_qr(data: str, size: int, transparent: bool = False) -> Image.Image:
    qr = qrcode.QRCode(border=1, box_size=10)
    qr.add_data(data)
    qr.make(fit=True)
    back_color = "transparent" if transparent else "white"
    img = qr.make_image(fill_color=PIA_GREEN, back_color=back_color)
    img = img.convert("RGBA") if transparent else img.convert("RGB")
    return img.resize((size, size), Image.LANCZOS)


def generate_front_card(name: str, unique_id: str, department: str,
                         photo_path: str, output_path: str,
                         template_path: str = FRONT_TEMPLATE_PATH):
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Card template not found at {template_path}")

    card = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(card)

    if photo_path and os.path.exists(photo_path):
        _paste_photo(card, photo_path, PHOTO_BOX)
    else:
        _draw_photo_placeholder(draw, PHOTO_BOX)

    font_name = _font("Carlito-Bold.ttf", 26)
    draw.text(NAME_POS, name.upper(), font=font_name, fill=PIA_GREEN, anchor="mm")

    font_heading = _font("Carlito-Bold.ttf", 20)
    draw.text(HEADING_POS, "INTERN", font=font_heading, fill=PIA_GOLD, anchor="mm")

    font_id = _font("Carlito-Bold.ttf", 18)
    draw.text(ID_LABEL_POS, f"ID No: {unique_id}", font=font_id, fill=PIA_GOLD, anchor="mm")

    dept_text = f"Department: {department}"
    font_dept = _fit_font(draw, dept_text, "Carlito-Bold.ttf", max_size=18, max_width=440)
    draw.text(DEPT_LABEL_POS, dept_text, font=font_dept, fill=PIA_GOLD, anchor="mm")

    qr_size = QR_BOX[2] - QR_BOX[0]
    qr_img = _make_qr(_verify_url(unique_id), qr_size)
    card.paste(qr_img, (QR_BOX[0], QR_BOX[1]), qr_img if qr_img.mode == "RGBA" else None)
    draw.rectangle(QR_BOX, outline=PIA_GREEN, width=2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    card.save(output_path, "PNG")
    return output_path


def generate_back_card(unique_id: str, issue_date: date, valid_until: date, output_path: str,
                        template_path: str = BACK_TEMPLATE_PATH):
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Back card template not found at {template_path}")

    card = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(card)

    font_bold = _font("Carlito-Bold.ttf", 18)
    font_caption = _font("Carlito-Italic.ttf", 13)

    draw.text(BACK_ISSUE_POS, f"Issue Date: {issue_date.strftime('%d-%b-%Y')}",
              font=font_bold, fill=PIA_GOLD, anchor="mm")
    draw.text(BACK_VALID_POS, f"Valid Until: {valid_until.strftime('%d-%b-%Y')}",
              font=font_bold, fill=PIA_GOLD, anchor="mm")

    qr_size = BACK_QR_BOX[2] - BACK_QR_BOX[0]
    qr_img = _make_qr(_verify_url(unique_id), qr_size)
    card.paste(qr_img, (BACK_QR_BOX[0], BACK_QR_BOX[1]), qr_img if qr_img.mode == "RGBA" else None)

    draw.text(BACK_CAPTION_POS, "Scan for attendance or verification",
              font=font_caption, fill="#555555", anchor="mm")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    card.save(output_path, "PNG")
    return output_path