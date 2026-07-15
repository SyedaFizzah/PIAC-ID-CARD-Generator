import io
import os
from datetime import date
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SECURITY_LETTER_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "security_letter_template.png")
OFFER_LETTER_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "offer_letter_template.png")
CERTIFICATE_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "certificate_template.png")

FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts")


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if "Bold" in name else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(fallback, size)


def _create_base_image(template_path: str, size=(2480, 3508), background="white"):
    if os.path.exists(template_path):
        return Image.open(template_path).convert("RGB")
    return Image.new("RGB", size, background)


def _draw_centered_text(draw: ImageDraw.ImageDraw, text: str, position: tuple[int, int], font: ImageFont.FreeTypeFont, fill="black"):
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    height = box[3] - box[1]
    x, y = position
    draw.text((x - width // 2, y - height // 2), text, font=font, fill=fill)


def _normalize_pronouns(gender: str | None) -> dict[str, str]:
    if gender:
        normalized = gender.strip().lower()
    else:
        normalized = ""

    if any(term in normalized for term in ["female", "f", "woman", "girl"]):
        return {
            "subject": "she",
            "object": "her",
            "possessive": "her",
            "title": "Ms.",
        }
    
    if any(term in normalized for term in [
        "prefer not to say",
        "non-binary",
        "nonbinary",
        "other",
    ]):
        return {
            "subject": "they",
            "object": "them",
            "possessive": "their",
            "title": "Mx.",
        }
    
    return {
        "subject": "he",
        "object": "him",
        "possessive": "his",
        "title": "Mr.",
    }
    
def _save_pdf(image: Image.Image) -> io.BytesIO:
    buffer = io.BytesIO()
    image.save(buffer, format="PDF", resolution=300.0)
    buffer.seek(0)
    return buffer


def generate_security_letter(intern, template_path: str = SECURITY_LETTER_TEMPLATE_PATH) -> io.BytesIO:
    card = _create_base_image(template_path)
    draw = ImageDraw.Draw(card)

    title_font = _font("Carlito-Bold.ttf", 52)
    heading_font = _font("Carlito-Bold.ttf", 30)
    body_font = _font("Carlito-Regular.ttf", 24)

    _draw_centered_text(draw, "Security Letter", (1240, 220), title_font, fill="#0A5C36")

    issue_date = date.today().strftime("%d %B %Y")
    draw.text((220, 320), f"Date: {issue_date}", font=body_font, fill="black")

    body_lines = [
        f"This is to certify that {intern.name}, holding Unique ID {intern.unique_id},",
        f"is currently an intern with Pakistan International Airlines (PIA).",
        f"The intern is enrolled in the {intern.department or 'N/A'} department and is responsible",
        f"for activities related to {intern.discipline or 'their discipline'} during the internship period.",
        "",
        f"The internship begins on {intern.start_date.strftime('%d %B %Y')} and is valid until",
        f"{intern.valid_until.strftime('%d %B %Y')} ({intern.duration_weeks} weeks).",
        "",
        "This letter is issued for security and access purposes only.",
        "",
        "Please present this letter to the relevant security personnel when requested.",
    ]

    y = 420
    for line in body_lines:
        draw.text((220, y), line, font=body_font, fill="black")
        y += 46

    _draw_centered_text(draw, "Authorized by PIA Security Office", (1240, y + 140), heading_font, fill="#A6873C")
    return _save_pdf(card)


def generate_offer_letter(intern, template_path: str = OFFER_LETTER_TEMPLATE_PATH) -> io.BytesIO:
    card = _create_base_image(template_path)
    draw = ImageDraw.Draw(card)

    title_font = _font("Carlito-Bold.ttf", 52)
    body_font = _font("Carlito-Regular.ttf", 24)
    heading_font = _font("Carlito-Bold.ttf", 30)

    pronouns = _normalize_pronouns(intern.gender)
    salutation = f"Dear {pronouns['title']} {intern.name},"

    _draw_centered_text(draw, "Offer Letter", (1240, 220), title_font, fill="#0A5C36")
    draw.text((220, 320), salutation, font=heading_font, fill="black")

    opening = [
        f"We are pleased to extend to you an offer for an internship at Pakistan International Airlines.",
        f"This offer is made in recognition of your academic background at {intern.university or 'your institution'}",
        f"and the potential contribution {pronouns['subject']} will bring to the {intern.department or 'PIA'} team.",
        "",
        f"Your internship begins on {intern.start_date.strftime('%d %B %Y')} and continues through",
        f"{intern.valid_until.strftime('%d %B %Y')}, for a total duration of {intern.duration_weeks} weeks.",
        "",
        f"During this period, {pronouns['subject']} is expected to follow all company policies and",
        f"procedures, and to conduct {pronouns['object']} duties in a professional manner.",
        "",
        "Please confirm your acceptance by signing and returning a copy of this letter.",
    ]

    y = 390
    for line in opening:
        draw.text((220, y), line, font=body_font, fill="black")
        y += 46

    _draw_centered_text(draw, "Sincerely,", (1240, y + 120), heading_font, fill="black")
    _draw_centered_text(draw, "Pakistan International Airlines", (1240, y + 190), body_font, fill="#0A5C36")
    return _save_pdf(card)


def generate_certificate(intern, template_path: str = CERTIFICATE_TEMPLATE_PATH) -> io.BytesIO:
    card = _create_base_image(template_path)
    draw = ImageDraw.Draw(card)

    title_font = _font("Carlito-Bold.ttf", 64)
    subtitle_font = _font("Carlito-Bold.ttf", 36)
    body_font = _font("Carlito-Regular.ttf", 26)

    _draw_centered_text(draw, "Certificate of Internship", (1240, 260), title_font, fill="#0A5C36")
    _draw_centered_text(draw, f"This is to certify that", (1240, 420), subtitle_font, fill="black")
    _draw_centered_text(draw, intern.name, (1240, 540), title_font, fill="#A6873C")

    certification_text = (
        f"has successfully completed an internship with Pakistan International Airlines from"
        f" {intern.start_date.strftime('%d %B %Y')} to {intern.valid_until.strftime('%d %B %Y')},"
        f" spanning {intern.duration_weeks} weeks."
    )
    draw.text((220, 680), certification_text, font=body_font, fill="black")

    if intern.department:
        draw.text((220, 760), f"Department: {intern.department}", font=body_font, fill="black")
    if intern.discipline:
        draw.text((220, 820), f"Discipline: {intern.discipline}", font=body_font, fill="black")

    _draw_centered_text(draw, "Presented by Pakistan International Airlines", (1240, 980), body_font, fill="#0A5C36")
    return _save_pdf(card)
