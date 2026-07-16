# Wiring the LaTeX templates into PIAC-ID-CARD-Generator

## File placement

```
backend/app/
├── card_generator.py              (unchanged — keep as-is)
├── certificate_generator.py       ← new, from this zip
├── security_letter_generator.py   ← new, from this zip
├── latex_templates/                ← unzip pia_latex_templates.zip's
│   ├── internship_letter/          internship_letter/ and security_letter/
│   └── security_letter/            folders here (skip card/ — not used)
└── routers/
    ├── cards.py                   (unchanged)
    ├── certificates.py            ← new, from this zip
    └── security_letters.py        ← new, from this zip
```

Register the two new routers in `main.py` next to wherever `cards.router` is
already included:

```python
from .routers import certificates, security_letters
app.include_router(certificates.router)
app.include_router(security_letters.router)
```

## paths.py additions

```python
CERT_DIR = os.path.join(DATA_DIR, "certificates")
SECURITY_LETTER_DIR = os.path.join(DATA_DIR, "security_letters")
os.makedirs(CERT_DIR, exist_ok=True)
os.makedirs(SECURITY_LETTER_DIR, exist_ok=True)
```
(matching whatever pattern `CARD_DIR` already follows there)

## Model changes needed

Your current `Intern` model (inferred from `cards.py`) has: `name`, `unique_id`,
`department`, `photo_path`, `start_date`, `valid_until`. The certificate template
needs a few fields it doesn't look like you're storing yet:

- `gender` ('male' / 'female') — controls pronouns in the certificate text
- `degree_title` (e.g. "Bachelor of Computer Science (AI)")
- `university_name`
- `project_description`
- `skills`
- `certificate_path` (to mirror `card_front_path`/`card_back_path`)

For the security letter, `Intern` needs a `cnic` field if it doesn't have one.

If you'd rather not add all of these as DB columns right away, an easier path
for `project_description`/`skills` is to accept them as request-body fields on
the `/generate-certificate` endpoint instead of pulling from the DB — only
`gender`, `degree_title`, `university_name`, and `cnic` are the ones you'd
actually want persisted since they don't change per-generation.

## Dependencies

```bash
pip install jinja2
```
Plus MiKTeX (for `xelatex`) on whatever machine runs this — same as discussed
for the standalone templates. `pdftoppm`/Poppler is NOT needed here since
neither of these routers converts to PNG (cards.py already returns
image/PDF directly; these two return PDF directly via FileResponse).

## Blocking call note

Both new routes are plain `def` (not `async def`), matching your `cards.py`
style — FastAPI runs those in a threadpool automatically, so the blocking
`subprocess.run(['xelatex', ...])` call (~300-500ms) won't stall the event
loop. Keep them as `def`, not `async def`.
