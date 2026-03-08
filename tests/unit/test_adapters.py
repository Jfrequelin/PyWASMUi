from __future__ import annotations

from pywasm_ui.adapters import _extract_flask_requested_token


class _FakeWs:
    def __init__(self, query: str | None = None) -> None:
        self.environ = {"QUERY_STRING": query} if query is not None else {}


def test_extract_flask_requested_token_from_query_string() -> None:
    ws = _FakeWs("session_token=abc123&x=1")
    assert _extract_flask_requested_token(ws) == "abc123"


def test_extract_flask_requested_token_returns_none_when_missing() -> None:
    ws = _FakeWs("x=1")
    assert _extract_flask_requested_token(ws) is None
