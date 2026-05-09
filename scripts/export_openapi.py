from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
VENV_PYTHON = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
DEFAULT_OUTPUT = ROOT_DIR / "docs" / "api" / "openapi.yaml"


def get_python() -> Path:
    if VENV_PYTHON.exists():
        return VENV_PYTHON
    return Path(sys.executable)


def dump_yaml(data: dict[str, Any]) -> str:
    try:
        import yaml
    except ImportError:
        return json.dumps(data, ensure_ascii=False, indent=2)
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def export_openapi(output: Path, python: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(python), "-c", f"""
import sys; sys.path.insert(0, r'{BACKEND_DIR}')
from app.main import app
import json
data = app.openapi()
print(json.dumps(data, ensure_ascii=False, indent=2))
"""],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    output.write_text(dump_yaml(json.loads(result.stdout)), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export FastAPI OpenAPI schema.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output file path. Defaults to {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--python",
        type=Path,
        default=get_python(),
        help="Python interpreter. Defaults to backend .venv python.",
    )
    args = parser.parse_args()
    export_openapi(args.output, args.python)
    print(f"OpenAPI schema exported to {args.output}")


if __name__ == "__main__":
    main()
