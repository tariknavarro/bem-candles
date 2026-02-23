"""
Entry-point opcional.

Uso:
  python main.py

Isso executa o mesmo que:
  streamlit run app.py
"""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())

