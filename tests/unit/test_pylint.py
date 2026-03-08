from __future__ import annotations

import subprocess
import sys
import importlib.util
from pathlib import Path

import pytest


def test_pylint_strict() -> None:
    if importlib.util.find_spec("pylint") is None:
        pytest.skip("pylint is not installed in this Python environment")

    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "python_lib" / "pywasm_ui",
        root / "server" / "app",
    ]

    cmd = [
        sys.executable,
        "-m",
        "pylint",
        "--fail-under=9.9",
        *(str(target) for target in targets),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        details = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
        raise AssertionError(f"pylint failed with exit code {result.returncode}\n{details}")
