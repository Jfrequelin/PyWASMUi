from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from pywasm_ui import page, register_fastapi_pages


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_register_fastapi_pages_supports_multipage_and_guard(tmp_path: Path) -> None:
    web_root = tmp_path / "web"
    _write(web_root / "index.html", "<h1>home</h1>")
    _write(web_root / "admin.html", "<h1>admin</h1>")

    app = FastAPI()
    register_fastapi_pages(
        app,
        web_root,
        [
            page("/", "index.html"),
            page(
                "/admin",
                "admin.html",
                guard=lambda request: request.headers.get("x-admin") == "1",
            ),
        ],
    )

    client = TestClient(app)

    home = client.get("/")
    assert home.status_code == 200
    assert "home" in home.text

    admin_forbidden = client.get("/admin")
    assert admin_forbidden.status_code == 403

    admin_allowed = client.get("/admin", headers={"x-admin": "1"})
    assert admin_allowed.status_code == 200
    assert "admin" in admin_allowed.text
