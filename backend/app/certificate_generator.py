"""
PIA Internship Certificate Generator

Wraps the LaTeX (letter.tex.jinja) template — same role as card_generator.py
plays for the ID card, just calling xelatex instead of Pillow.

Place this file at: backend/app/certificate_generator.py
Place the latex_templates/ folder at: backend/app/latex_templates/
"""
import os
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
LATEX_DIR = os.path.join(BASE_DIR, "templates", "internship_letter")
LETTERHEAD_PATH = os.path.join(LATEX_DIR, "assets", "letterhead.jpeg")

_env = Environment(
    block_start_string=r'\BLOCK{', block_end_string='}',
    variable_start_string=r'\VAR{', variable_end_string='}',
    comment_start_string=r'\#{', comment_end_string='}',
    line_statement_prefix='%%', line_comment_prefix='%#',
    trim_blocks=True, autoescape=False,
    loader=FileSystemLoader(LATEX_DIR),
)

_PRONOUNS = {
    'male':   dict(pronoun_subject='he', pronoun_subject_cap='He',
                   pronoun_object='him', pronoun_possessive='his', pronoun_possessive_cap='His'),
    'female': dict(pronoun_subject='she', pronoun_subject_cap='She',
                   pronoun_object='her', pronoun_possessive='her', pronoun_possessive_cap='Her'),
}


def _escape(s):
    if not isinstance(s, str):
        return s
    for k, v in {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                 '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'}.items():
        s = s.replace(k, v)
    return s


def generate_certificate(intern, output_dir: str) -> str:
    """
    intern must provide: name, gender ('male'/'female'), degree_title,
    university_name, start_date, valid_until, department,
    project_description, skills, unique_id.
    Returns path to the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    template = _env.get_template('letter.tex.jinja')

    data = {
        'recipient_title': 'Mr.' if intern.gender == 'male' else 'Ms.',
        'recipient_name': intern.name,
        'degree_title': intern.degree_title,
        'university_name': intern.university_name,
        'issue_date': intern.valid_until.strftime('%d %B, %Y'),
        'duration_text': f"{(intern.valid_until - intern.start_date).days // 30} Months",
        'start_date': intern.start_date.strftime('%dth %B %Y'),
        'end_date': intern.valid_until.strftime('%dth %B %Y'),
        'department': intern.department,
        'project_description': intern.project_description,
        'skills': intern.skills,
        'signatory_title': 'GM Information Technology',
        'signatory_name': 'Waqas Ahmed',
        'letterhead_path': LETTERHEAD_PATH.replace('\\', '/'),  # xelatex wants forward slashes even on Windows
    }
    ctx = {**_PRONOUNS[intern.gender], **{k: _escape(v) for k, v in data.items() if k != 'letterhead_path'}}
    ctx['letterhead_path'] = data['letterhead_path']

    tex_source = template.render(**ctx)
    tex_path = os.path.join(output_dir, f"{intern.unique_id}_certificate.tex")
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex_source)

    result = subprocess.run(
        ['xelatex', '-interaction=nonstopmode', '-halt-on-error', os.path.basename(tex_path)],
        cwd=output_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"xelatex failed for {intern.unique_id}:\n{result.stdout[-2000:]}")

    return os.path.join(output_dir, f"{intern.unique_id}_certificate.pdf")
