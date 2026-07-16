"""
PIA Security Entry-Permission Letter Generator

Wraps security_letter.tex.jinja. No letterhead/background — plain A4.

Place this file at: backend/app/security_letter_generator.py
"""
import os
import subprocess
from datetime import date
from jinja2 import Environment, FileSystemLoader
import models

BASE_DIR = os.path.dirname(__file__)
LATEX_DIR = os.path.join(BASE_DIR, "templates", "security_letter")

MAX_CANDIDATES = 15
MIN_CANDIDATES = 0

_env = Environment(
    block_start_string=r'\BLOCK{', block_end_string='}',
    variable_start_string=r'\VAR{', variable_end_string='}',
    comment_start_string=r'\#{', comment_end_string='}',
    line_statement_prefix='%%', line_comment_prefix='%#',
    trim_blocks=True, autoescape=False,
    loader=FileSystemLoader(LATEX_DIR),
)


def _escape(s):
    if not isinstance(s, str):
        return s
    for k, v in {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                 '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'}.items():
        s = s.replace(k, v)
    return s


def generate_security_letter(interns: list, section_name: str, supervisor_title: str,
                              start_date: date, end_date: date, output_dir: str,
                              file_stub: str = None) -> str:
    """
    interns: list of Intern ORM objects (needs .name and .cnic) — 0 to 15 of them.
    Returns path to the generated PDF.
    """
    if len(interns) > MAX_CANDIDATES:
        raise ValueError(f"Too many candidates: got {len(interns)}, max is {MAX_CANDIDATES}.")
    if len(interns) < MIN_CANDIDATES:
        raise ValueError("Candidate count cannot be negative.")

    os.makedirs(output_dir, exist_ok=True)
    template = _env.get_template('security_letter.tex.jinja')

    file_stub = file_stub or f"security_letter_{date.today().isoformat()}"
    ctx = {
        'issue_date': date.today().strftime('%d-%B-%Y'),
        'subject_line': _escape('Permission for Entry of Internship Students'),
        'section_name': _escape(section_name),
        'supervisor_title': _escape(supervisor_title),
        'start_date': start_date.strftime('%B %d, %Y'),
        'end_date': end_date.strftime('%B %d, %Y'),
        'signatory_name': _escape(s.name) for s in supervisors if isinstance(s, models.Supervisor) else _escape(s.name) for s in managers if isinstance(s, models.Manager),
        'signatory_title': _escape(s.designation),
        'candidates': [{'name': _escape(i.name), 'cnic': _escape(i.cnic)} for i in interns],
    }

    tex_source = template.render(**ctx)
    tex_path = os.path.join(output_dir, f"{file_stub}.tex")
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex_source)

    result = subprocess.run(
        ['xelatex', '-interaction=nonstopmode', '-halt-on-error', os.path.basename(tex_path)],
        cwd=output_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"xelatex failed for {file_stub}:\n{result.stdout[-2000:]}")

    return os.path.join(output_dir, f"{file_stub}.pdf")
