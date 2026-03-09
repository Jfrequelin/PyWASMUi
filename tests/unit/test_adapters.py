from __future__ import annotations

from pywasm_ui.adapters import _extract_flask_requested_token
from pywasm_ui.frontend_assets import get_packaged_frontend_root


class _FakeWs:
    def __init__(self, query: str | None = None) -> None:
        self.environ = {"QUERY_STRING": query} if query is not None else {}


def test_extract_flask_requested_token_from_query_string() -> None:
    ws = _FakeWs("session_token=abc123&x=1")
    assert _extract_flask_requested_token(ws) == "abc123"


def test_extract_flask_requested_token_returns_none_when_missing() -> None:
    ws = _FakeWs("x=1")
    assert _extract_flask_requested_token(ws) is None


def test_get_packaged_frontend_root_contains_runtime_assets() -> None:
    root = get_packaged_frontend_root()
    assert root.is_dir()
    assert (root / "src" / "main.js").is_file()
    assert (root / "wasm_ui" / "pkg" / "wasm_ui.js").is_file()
    assert (root / "wasm_ui" / "pkg" / "wasm_ui_bg.wasm").is_file()
