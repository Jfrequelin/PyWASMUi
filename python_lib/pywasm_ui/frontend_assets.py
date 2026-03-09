from __future__ import annotations

from pathlib import Path


def get_packaged_frontend_root() -> Path:
    """Return the directory that contains packaged pyWasm frontend assets."""

    root = Path(__file__).resolve().parent / "frontend"
    if not root.exists():
        raise RuntimeError("Packaged frontend assets are missing")
    return root
