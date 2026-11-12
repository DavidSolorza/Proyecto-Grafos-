"""Static audit of section 14: code comments and docstrings must be written in English."""
import ast
import io
import re
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPANISH_WORDS = re.compile(r"\b(el|la|los|las|que|para|con|una|del|por|como|cuando)\b", re.I)
SPANISH_LETTERS = re.compile(r"[áéíóúñ¿¡]")


def python_files() -> list[Path]:
    roots = [ROOT / "backend" / "src", ROOT / "backend" / "tests", ROOT / "backend" / "audit", ROOT / "desktop"]
    files = [f for r in roots for f in r.rglob("*.py") if "__pycache__" not in f.parts]
    return files + [ROOT / "backend" / "run.py", ROOT / "backend" / "verificar.py", ROOT / "backend" / "auditar_enunciado.py"]


def comments_and_docstrings(source: str) -> list[tuple[int, str]]:
    found = [(tok.start[0], tok.string) for tok in tokenize.generate_tokens(io.StringIO(source).readline)
             if tok.type == tokenize.COMMENT]
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                found.append((getattr(node, "lineno", 1), doc.splitlines()[0]))
    return found


def spanish_comments() -> list[str]:
    """Comments or docstring first lines that look Spanish (quoted fragments such as UI strings are ignored)."""
    hits = []
    for path in python_files():
        for line, text in comments_and_docstrings(path.read_text(encoding="utf-8")):
            body = re.sub(r"[`'\"].*?[`'\"]", "", text)
            if SPANISH_LETTERS.search(body) or len(SPANISH_WORDS.findall(body)) >= 2:
                hits.append(f"{path.name}:{line}: {text[:60]}")
    return hits


STYLES = ROOT / "frontend" / "src" / "styles"
FIXED_FONT = re.compile(r"font-size:\s*[\d.]+(px|rem)\b")
INLINE_FONT = re.compile(r"fontSize:\s*['\"]")


def fluid_css_report() -> tuple[int, list[str]]:
    """Web design rule: sizes are fluid. Returns (number of clamp() uses, fixed font sizes found)."""
    clamps, fixed = 0, []
    for css in sorted(STYLES.glob("*.css")):
        text = css.read_text(encoding="utf-8")
        clamps += text.count("clamp(")
        fixed += [f"{css.name}: {m.group(0)}" for m in FIXED_FONT.finditer(text)]
    for jsx in (ROOT / "frontend" / "src").rglob("*.jsx"):
        fixed += [f"{jsx.name}: inline {m.group(0)}" for m in INLINE_FONT.finditer(jsx.read_text(encoding="utf-8"))]
    return clamps, fixed
