from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from pywasm_ui.adapters import (
    _apply_security_headers,
    _extract_flask_requested_token,
    _is_origin_allowed,
    bootstrap_fastapi_app,
)
from pywasm_ui.frontend_assets import get_packaged_frontend_root
from pywasm_ui.widgets import ButtonWidget, LabelWidget


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


def test_bootstrap_fastapi_app_wires_routes_assets_and_websocket(tmp_path: Path) -> None:
    web_root = tmp_path / "web"
    web_root.mkdir(parents=True)
    (web_root / "index.html").write_text("<html><body>home</body></html>", encoding="utf-8")

    app = FastAPI()
    bootstrap_fastapi_app(
        app,
        web_root,
        server_secret="test-secret",
        initial_widgets=[
            LabelWidget(id="label1", parent="root", text="0"),
            ButtonWidget(id="btn1", parent="root", text="+1"),
        ],
    )
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    home = client.get("/")
    assert home.status_code == 200
    assert "home" in home.text

    asset = client.get("/pywasm-assets/src/main.js")
    assert asset.status_code == 200

    with client.websocket_connect("/ws") as ws:
        init = json.loads(ws.receive_text())
        assert init["type"] == "init"
