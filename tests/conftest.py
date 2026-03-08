from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_LIB = ROOT / "python_lib"

for path in (str(ROOT), str(PYTHON_LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)
