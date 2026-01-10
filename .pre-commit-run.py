#!/usr/bin/env python3
"""Cross-platform pre-commit runner that uses virtual environment tools."""

import subprocess
import sys
from pathlib import Path


def get_venv_python():
    """Get the Python executable in the virtual environment."""
    venv_path = Path(".venv")
    if sys.platform == "win32":
        python = venv_path / "Scripts" / "python.exe"
    else:
        python = venv_path / "bin" / "python"

    if not python.exists():
        print(f"Error: Virtual environment not found at {python}", file=sys.stderr)
        sys.exit(1)

    return str(python)


def main():
    tool = sys.argv[1]
    venv_python = get_venv_python()

    if tool == "mypy":
        cmd = [venv_python, "-m", "mypy"] + sys.argv[2:]
    elif tool == "pytest":
        cmd = [venv_python, "-m", "pytest"]
    else:
        print(f"Unknown tool: {tool}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
