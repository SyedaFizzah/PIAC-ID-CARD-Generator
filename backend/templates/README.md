# LaTeX templates — PIA intern ID card, internship certificate, security letter

Three self-contained templates, each with its own `generate_*.py` you can run standalone
(`python generate_card.py` etc.) to see a working example before wiring into FastAPI.

```
latex_templates/
├── card/
│   ├── card.tex.jinja
│   ├── generate_card.py
│   └── assets/ (sample_photo.png, sample_qr.png)
├── internship_letter/
│   ├── letter.tex.jinja
│   ├── generate_letter.py
│   └── assets/letterhead.jpeg
└── security_letter/
    ├── security_letter.tex.jinja
    ├── generate_security_letter.py
    └── assets/letterhead.jpeg
```

## Prerequisites (Windows)

1. **MiKTeX** (lighter than TeX Live): https://miktex.org/download — install, let it auto-install
   missing packages on first compile (`fontspec`, `eso-pic`, `booktabs`, `tikz`).
2. **Poppler for Windows** (for `pdftoppm`/PDF→PNG): download a build (e.g. from
   `oschwartz10612/poppler-windows` on GitHub), add its `bin/` to PATH.
3. `pip install jinja2`
4. Fonts used (`Arial`, `Times New Roman`) already ship with Windows — no extra installs needed there.
   If you move this to a Linux server later, swap `\setmainfont{Arial}` → `\setmainfont{Liberation Sans}`
   (or whatever's installed — check with `fc-list`), since Arial/Times aren't present on Linux by default.

## Why Jinja2 delimiters look unusual

Standard Jinja2 uses `{{ }}` and `{% %}`, which collide with LaTeX's own `{ }` grouping. All three
templates use the common LaTeX+Jinja2 convention instead:

| Jinja2 default | Used here |
|---|---|
| `{{ var }}` | `\VAR{var}` |
| `{% for x in y %}` | `\BLOCK{for x in y}` |
| `{# comment #}` | `\#{comment}` |

This is configured once in each `generate_*.py` via the `Environment(...)` constructor — you don't
need to touch it, just write `\VAR{}` / `\BLOCK{}` in the `.tex.jinja` files.

## Integrating into your FastAPI backend

Each `generate_*.py` exposes one function you can import directly:

```python
# in your FastAPI route
from card.generate_card import render_card
from internship_letter.generate_letter import render_letter
from security_letter.generate_security_letter import render_security_letter, MAX_CANDIDATES

@app.post("/api/interns/{intern_id}/card")
def create_card(intern_id: str, db: Session = Depends(get_db)):
    intern = get_intern_or_404(db, intern_id)

    # 1. generate QR (you already have this with `qrcode`)
    qr_path = generate_qr_for_intern(intern)          # -> saves PNG, returns path

    # 2. resolve uploaded photo path (already on disk from your upload endpoint)
    photo_path = intern.photo_path

    pdf_path = render_card({
        "name": intern.full_name,
        "designation": intern.designation,
        "intern_id": intern.id,
        "department": intern.department,
        "valid_upto": intern.valid_until.strftime("%d-%m-%Y"),
        "photo_path": photo_path,
        "qr_path": qr_path,
    }, out_dir=Path(f"generated/cards/{intern.id}"))

    return FileResponse(pdf_path)
```

The security-letter one is the one with the 0–15 rule already enforced *before* any LaTeX runs
(`render_security_letter` raises `ValueError` if `len(candidates) > 15`) — so add a matching check
on your Pydantic request model too, to fail fast with a clean 422 instead of a raw ValueError:

```python
from pydantic import BaseModel, conlist

class Candidate(BaseModel):
    name: str
    cnic: str

class SecurityLetterRequest(BaseModel):
    candidates: conlist(Candidate, min_length=0, max_length=15)
    start_date: str
    end_date: str
    # ...
```

On the frontend, this maps naturally to a table where "Add candidate" disables itself at 15 rows
and there's no minimum — an empty table still renders (shows "No candidates listed" instead of an
empty `tabular`, which is what the `\BLOCK{if candidates}` / `\BLOCK{else}` branch in the template
handles).

## Compiling — what happens under the hood

Each `render_*` function does the same three steps:
1. `template.render(**ctx)` → produces a `.tex` string with all `\VAR{}`/`\BLOCK{}` resolved.
2. Writes it to disk, then runs `xelatex -interaction=nonstopmode -halt-on-error file.tex` via
   `subprocess.run`. `xelatex` (not `pdflatex`) is required because `fontspec` needs it to load
   system fonts like Arial/Times New Roman directly.
3. (Card only) converts the resulting PDF to PNG with `pdftoppm` at 300 DPI, since your React
   frontend will want an image to preview inline rather than embedding a PDF viewer.

One compile pass is enough for all three — none of them use cross-references, a TOC, or anything
else that needs a second pass to resolve.

## Notes on the ID card layout

The card template is TikZ-based, sized exactly to CR80 (85.6mm × 54mm) so it prints correctly on
standard PVC card stock without scaling. Swoosh, sidebar color, and font sizes are all early
in the file if you want to tune them against the real Canva template — I built it from your
screenshot description (green sidebar, PIA logo, photo box, diagonal blue swoosh, red "Valid
Upto") rather than exact pixel measurements, so treat the colors/positions as a first pass to
adjust once you compare side-by-side with the real design.
