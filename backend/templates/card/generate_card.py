"""
Renders one intern ID card from card.tex.jinja and compiles it to PDF (+PNG) with xelatex.
Usage: python generate_card.py
"""
import subprocess
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

HERE = Path(__file__).parent

# Jinja2 env configured with LaTeX-safe delimiters so {} and \ don't clash with Jinja syntax
latex_jinja_env = Environment(
    block_start_string=r'\BLOCK{',
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=FileSystemLoader(str(HERE)),
)


def latex_escape(s: str) -> str:
    """Escape LaTeX special chars in user-supplied strings (names, departments, etc.)."""
    if s is None:
        return ""
    replacements = {
        '\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
        '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
        '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s


def render_card(intern: dict, out_dir: Path) -> Path:
    """intern needs: name, designation, intern_id, department, valid_upto, photo_path, qr_path"""
    out_dir.mkdir(parents=True, exist_ok=True)
    template = latex_jinja_env.get_template('card.tex.jinja')

    ctx = {k: latex_escape(v) if isinstance(v, str) else v for k, v in intern.items()}
    # photo_path / qr_path must NOT be escaped (they're file paths, not display text)
    ctx['photo_path'] = intern.get('photo_path')
    ctx['qr_path'] = intern.get('qr_path')

    tex_source = template.render(**ctx)
    tex_file = out_dir / f"{intern['intern_id']}.tex"
    tex_file.write_text(tex_source, encoding='utf-8')

    # Compile — run twice is unnecessary here (no refs/TOC), one pass is enough
    result = subprocess.run(
        ['xelatex', '-interaction=nonstopmode', '-halt-on-error', tex_file.name],
        cwd=out_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout[-3000:])
        raise RuntimeError(f"xelatex failed for {intern['intern_id']}")

    pdf_path = out_dir / f"{intern['intern_id']}.pdf"

    # Convert to PNG for web preview (frontend can't render PDF inline easily)
    subprocess.run(
        ['pdftoppm', '-png', '-r', '300', pdf_path.name, intern['intern_id']],
        cwd=out_dir, check=True
    )
    return pdf_path


if __name__ == '__main__':
    out = HERE / 'build'
    if out.exists():
        shutil.rmtree(out)

    sample = {
        'name': 'Syeda Fizzah Masroor',
        'designation': 'AI/ML Intern',
        'intern_id': 'PIA-INT-0142',
        'department': 'ERP Section',
        'valid_upto': '09-04-2027',
        'photo_path': str(HERE / 'assets' / 'sample_photo.png'),
        'qr_path': str(HERE / 'assets' / 'sample_qr.png'),
    }
    pdf = render_card(sample, out)
    print(f"Built: {pdf}")
