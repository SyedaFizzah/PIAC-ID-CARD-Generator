import subprocess
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).parent

latex_jinja_env = Environment(
    block_start_string=r'\BLOCK{', block_end_string='}',
    variable_start_string=r'\VAR{', variable_end_string='}',
    comment_start_string=r'\#{', comment_end_string='}',
    line_statement_prefix='%%', line_comment_prefix='%#',
    trim_blocks=True, autoescape=False,
    loader=FileSystemLoader(str(HERE)),
)

PRONOUNS = {
    'male':   dict(pronoun_subject='he', pronoun_subject_cap='He',
                   pronoun_object='him', pronoun_possessive='his', pronoun_possessive_cap='His'),
    'female': dict(pronoun_subject='she', pronoun_subject_cap='She',
                   pronoun_object='her', pronoun_possessive='her', pronoun_possessive_cap='Her'),
}


def latex_escape(s):
    if not isinstance(s, str):
        return s
    for k, v in {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                 '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'}.items():
        s = s.replace(k, v)
    return s


def render_letter(data: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    template = latex_jinja_env.get_template('letter.tex.jinja')

    ctx = {**PRONOUNS[data.pop('gender')], **data}
    ctx = {k: (latex_escape(v) if k != 'letterhead_path' else v) for k, v in ctx.items()}

    tex_source = template.render(**ctx)
    tex_file = out_dir / f"{data['file_stub']}.tex"
    tex_file.write_text(tex_source, encoding='utf-8')

    result = subprocess.run(
        ['xelatex', '-interaction=nonstopmode', '-halt-on-error', tex_file.name],
        cwd=out_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout[-3000:])
        raise RuntimeError("xelatex failed")
    return out_dir / f"{data['file_stub']}.pdf"


if __name__ == '__main__':
    out = HERE / 'build'
    if out.exists():
        shutil.rmtree(out)

    sample = {
        'file_stub': 'sample_letter',
        'gender': 'female',
        'recipient_title': 'Ms.',
        'recipient_name': 'Syeda Fizzah Masroor',
        'degree_title': 'Bachelor of Computer Science (AI)',
        'university_name': 'NED University of Engineering and Technology',
        'issue_date': '04 September, 2026',
        'duration_text': 'Two Months',
        'start_date': '08th July 2026',
        'end_date': '04th September 2026',
        'department': 'ERP Section',
        'project_description': 'the intern ID card generation system and AI email assistant',
        'skills': 'Python, FastAPI, React, and PostgreSQL',
        'signatory_title': 'GM Information Technology',
        'signatory_name': 'Waqas Ahmed',
        'letterhead_path': str(HERE / 'assets' / 'letterhead.jpeg'),
    }
    pdf = render_letter(sample, out)
    print(f"Built: {pdf}")
