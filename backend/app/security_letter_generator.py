import os
import subprocess
from datetime import date
from jinja2 import Environment, FileSystemLoader
from . import models

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


def _resolve_signatory(session, department: str):
    """
    Find the Supervisor responsible for the given department.
    department strings must match exactly (case-sensitive) between
    Intern.department and Supervisor.department.
    """
    supervisor = (
        session.query(models.Supervisor)
        .filter(models.Supervisor.department == department)
        .first()
    )
    if not supervisor:
        raise ValueError(f"No supervisor found for department '{department}'.")
    return supervisor



def generate_security_letter(interns: list, department: str,
                              start_date: date, end_date: date, output_dir: str,
                              session, file_stub: str = None) -> str:
    """
    interns: list of Intern ORM objects (needs .name and .cnic) — 0 to 15 of them,
             all belonging to the SAME department.
    department: the intern department (used as section_name in the letter, and to look up the correct Supervisor).
    session: SQLAlchemy session, used to resolve the correct signatory.
    Returns path to the generated PDF.
    """
    if len(interns) > MAX_CANDIDATES:
        raise ValueError(f"Too many candidates: got {len(interns)}, max is {MAX_CANDIDATES}.")
    if len(interns) < MIN_CANDIDATES:
        raise ValueError("Candidate count cannot be negative.")

    # Guard against silently mixing departments in one letter —
    # all interns MUST match the department passed in.
    mismatched = [i for i in interns if i.department != department]
    if mismatched:
        names = ', '.join(i.name for i in mismatched)
        raise ValueError(
            f"These interns don't belong to department '{department}': {names}. "
            "Group interns by department before generating a letter."
        )

    # cnic is nullable in the schema — decide if that's acceptable for a security letter
    missing_cnic = [i.name for i in interns if not i.cnic]
    if missing_cnic:
        raise ValueError(
            f"These interns are missing a CNIC, required for the security letter: "
            f"{', '.join(missing_cnic)}"
        )

    supervisor = _resolve_signatory(session, department)

    os.makedirs(output_dir, exist_ok=True)
    template = _env.get_template('security_letter.tex.jinja')

    file_stub = file_stub or f"security_letter_{date.today().isoformat()}"
    ctx = {
        'issue_date': date.today().strftime('%d-%B-%Y'),
        'subject_line': _escape('Permission for Entry of Internship Students'),
        'section_name': _escape(department),
        'supervisor_title': _escape(supervisor.designation),
        'start_date': start_date.strftime('%B %d, %Y'),
        'end_date': end_date.strftime('%B %d, %Y'),
        'signatory_name': _escape(supervisor.name),
        'signatory_title': _escape(supervisor.designation),
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