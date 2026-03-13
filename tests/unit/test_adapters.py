from __future__ import annotations

from pywasm_ui.adapters import (
    _apply_security_headers,
    _extract_flask_requested_token,
    _is_origin_allowed,
)
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


def test_is_origin_allowed_respects_allow_list() -> None:
    allowed = {"https://example.com"}

    assert _is_origin_allowed("https://example.com", allowed)
    assert not _is_origin_allowed("https://evil.example", allowed)
    assert not _is_origin_allowed(None, allowed)


def test_apply_security_headers_adds_defaults_once() -> None:
    class _Response:
        def __init__(self) -> None:
            self.headers: dict[str, str] = {}

    response = _Response()
    _apply_security_headers(response)
    _apply_security_headers(response)

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
