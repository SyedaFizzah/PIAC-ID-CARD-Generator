import os

BASE_DIR = os.path.dirname(__file__)

PHOTO_DIR = os.path.join(BASE_DIR, "static", "photos")
CARD_DIR = os.path.join(BASE_DIR, "static", "cards")

CERT_DIR = os.path.join(BASE_DIR, "static", "certificates")
SECURITY_LETTER_DIR = os.path.join(BASE_DIR, "static", "security_letters")
os.makedirs(CERT_DIR, exist_ok=True)
os.makedirs(SECURITY_LETTER_DIR, exist_ok=True)