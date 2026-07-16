import subprocess
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).parent
MAX_CANDIDATES = 15
MIN_CANDIDATES = 0

latex_jinja_env = Environment(
    block_start_string=r'\BLOCK{', block_end_string='}',
    variable_start_string=r'\VAR{', variable_end_string='}',
    comment_start_string=r'\#{', comment_end_string='}',
    line_statement_prefix='%%', line_comment_prefix='%#',
    trim_blocks=True, autoescape=False,
    loader=FileSystemLoader(str(HERE)),
)


def latex_escape(s):
    if not isinstance(s, str):
        return s
    for k, v in {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                 '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}'}.items():
        s = s.replace(k, v)
    return s


def render_security_letter(data: dict, out_dir: Path) -> Path:
    candidates = data.get('candidates', [])

    # --- enforce 0-15 candidate range before touching LaTeX at all ---
    if len(candidates) > MAX_CANDIDATES:
        raise ValueError(
            f"Too many candidates: got {len(candidates)}, max is {MAX_CANDIDATES}."
        )
    if len(candidates) < MIN_CANDIDATES:
        raise ValueError("Candidate count cannot be negative.")

    out_dir.mkdir(parents=True, exist_ok=True)
    template = latex_jinja_env.get_template('security_letter.tex.jinja')

    ctx = {k: (latex_escape(v) if k not in ('candidates', 'letterhead_path') else v)
           for k, v in data.items()}
    ctx['candidates'] = [
        {'name': latex_escape(c['name']), 'cnic': latex_escape(c['cnic'])}
        for c in candidates
    ]

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
        'file_stub': 'sample_security_letter',
        'issue_date': '08-July-2026',
        'subject_line': 'Permission for Entry of Internship Students',
        'section_name': 'ERP Section',
        'supervisor_title': 'Manager Information Technology',
        'start_date': 'July 08, 2026',
        'end_date': 'September 04, 2026',
        'signatory_name': 'Waqas Ahmed',
        'signatory_title': 'GM Information Technology',
        'candidates': [
            {'name': 'Danish Ali', 'cnic': '43205-9877317-7'},
            {'name': 'Muhammad Shaheer', 'cnic': '42201-6556637-3'},
            {'name': 'Sheikh Muhammad Abdullah', 'cnic': '42101-3835092-1'},
            {'name': 'Syeda Fizzah Masroor', 'cnic': '42101-0885515-4'},
        ],
    }
    pdf = render_security_letter(sample, out)
    print(f"Built: {pdf}")
