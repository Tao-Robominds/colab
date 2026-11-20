import ast
from pathlib import Path
import tokenize


def audit_code(root: Path) -> dict:
    violations = []
    checked = []
    skipped_roots = {".git", ".venv", "venv", "__pycache__", "pipeline", "sam4tun"}
    for path in sorted(root.rglob("*.py")):
        if any(part in skipped_roots for part in path.parts):
            continue
        checked.append(str(path.relative_to(root)))
        with tokenize.open(path) as stream:
            source = stream.read()
        with path.open("rb") as stream:
            for token in tokenize.tokenize(stream.readline):
                if token.type == tokenize.COMMENT:
                    violations.append((str(path.relative_to(root)), token.start[0], "comment"))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and ast.get_docstring(node, clean=False) is not None:
                violations.append((str(path.relative_to(root)), getattr(node, "lineno", 1), "docstring"))
    return {"checked_files": len(checked), "violations": violations, "passed": bool(checked) and not violations}
