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

def _ordinal_date(d) -> str:
    day = d.day
    suffix = 'th' if 11 <= day % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return d.strftime(f'%-d{suffix} %B %Y') if os.name != 'nt' else d.strftime(f'%#d{suffix} %B %Y')
   

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

def _get_intern_or_404(intern_id: int, db: Session) -> Intern:
    if not (intern := db.query(Intern).filter(Intern.id == intern_id).first()):
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern

if __name__ == '__main__':
    out = HERE / 'build'
    if out.exists():
        shutil.rmtree(out)

data = {
        'recipient_title': _TITLES[gender_key],
        'recipient_name': intern.name,
        'degree_title': intern.degree_title,
        'university_name': intern.university_name,
        'issue_date': _ordinal_date(intern.valid_until),
        'start_date': _ordinal_date(intern.start_date),
        'end_date': _ordinal_date(intern.valid_until),
        'department': intern.department,
        'project_description': intern.project_description,
        'skills': intern.skills,
        'signatory_title': supervisor.designation,
        'signatory_name': supervisor.name,
        'letterhead_path': LETTERHEAD_PATH.replace('\\', '/'),
    }


pdf = render_letter(sample, out)
print(f"Built: {pdf}")
