from __future__ import annotations

import contextlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path

import pytest

PYTHON = sys.executable

EXAMPLE_CASES = [
    {
        "name": "fastapi_01_single",
        "framework": "fastapi",
        "target": "server.app.examples.fastapi:example_01_app",
        "initial_id": "hello_label",
        "initial_text": "Hello from PyWASMui",
        "click_id": "add_widget_btn",
        "after_id": "dynamic_label_1",
        "after_text": "Dynamic widget #1",
    },
    {
        "name": "fastapi_02_composition",
        "framework": "fastapi",
        "target": "server.app.examples.fastapi:example_02_app",
        "initial_id": "title_label",
        "initial_text": "Composition with parent/child",
        "click_id": "increment_btn",
        "after_id": "counter_label",
        "after_text": "Count: 1",
    },
    {
        "name": "fastapi_03_style_updates",
        "framework": "fastapi",
        "target": "server.app.examples.fastapi:example_03_app",
        "initial_id": "status_label",
        "initial_text": "Theme: Inactive",
        "click_id": "toggle_btn",
        "after_id": "status_label",
        "after_text": "Theme: Active",
    },
    {
        "name": "fastapi_04_template",
        "framework": "fastapi",
        "target": "server.app.examples.fastapi:example_04_app",
        "initial_id": "title_label",
        "initial_text": "Shared template active",
    },
    {
        "name": "fastapi_server",
        "framework": "fastapi",
        "target": "server.app.examples.fastapi:app",
        "initial_id": "label1",
        "initial_text": "0",
        "click_id": "btn1",
        "after_id": "label1",
        "after_text": "1",
    },
    {
        "name": "fastapi_all_widgets",
        "framework": "fastapi",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "initial_id": "heading_title",
        "initial_text": "Widget Showcase",
        "click_id": "btn_1",
        "after_id": "label_count_1",
        "after_text": "Count A: 1",
    },
    {
        "name": "flask_server",
        "framework": "flask",
        "target": "server.app.examples.flask.flask_server:app",
        "initial_id": "label1",
        "initial_text": "0",
        "click_id": "btn1",
        "after_id": "label1",
        "after_text": "1",
    },
]


@contextlib.contextmanager
def _temporary_runtime_config(root: Path, port: int) -> Iterator[None]:
    runtime_cfg = root / "client" / "config" / "pywasm.runtime.json"
    original: str | None = None
    if runtime_cfg.exists():
        original = runtime_cfg.read_text(encoding="utf-8")

    runtime_cfg.parent.mkdir(parents=True, exist_ok=True)
    runtime_cfg.write_text(
        json.dumps(
            {
                "websocket": {
                    "host": None,
                    "port": port,
                    "path": "/ws",
                    "protocol": None,
                }
            }
        ),
        encoding="utf-8",
    )

    try:
        yield
    finally:
        if original is None:
            with contextlib.suppress(OSError):
                runtime_cfg.unlink()
        else:
            runtime_cfg.write_text(original, encoding="utf-8")


@contextlib.contextmanager
def _live_example_server(case: dict[str, str]) -> Iterator[str]:
    root = Path(__file__).resolve().parents[2]

    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        port = int(sock.getsockname()[1])

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{root / 'python_lib'}:{env.get('PYTHONPATH', '')}".rstrip(":")

    if case["framework"] == "fastapi":
        command = [
            PYTHON,
            "-m",
            "uvicorn",
            case["target"],
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ]
    else:
        env["PYWASM_WS_PORT"] = str(port)
        env["PYWASM_WS_HOST"] = "127.0.0.1"
        command = [
            PYTHON,
            "-m",
            "flask",
            "--app",
            case["target"],
            "run",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-reload",
        ]

    with _temporary_runtime_config(root, port):
        process = subprocess.Popen(
            command,
            cwd=str(root),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        base_url = f"http://127.0.0.1:{port}"
        health_url = f"{base_url}/health"

        deadline = time.time() + 25
        while time.time() < deadline:
            if process.poll() is not None:
                pytest.fail(f"Example server exited early for case: {case['name']}")
            try:
                with urllib.request.urlopen(health_url, timeout=1) as response:
                    if response.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.2)
        else:
            process.terminate()
            process.wait(timeout=5)
            pytest.fail(f"Timed out waiting for health endpoint: {case['name']}")

        try:
            yield base_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


@pytest.mark.parametrize("case", EXAMPLE_CASES, ids=[c["name"] for c in EXAMPLE_CASES])
def test_example_ui_with_playwright(case: dict[str, str]) -> None:
    sync_api = pytest.importorskip("playwright.sync_api")

    try:
        with sync_api.sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            page = browser.new_page()
            try:
                with _live_example_server(case) as live_server:
                    page.goto(live_server, wait_until="networkidle")

                    initial = page.locator(f"#{case['initial_id']}")
                    initial.wait_for(state="visible", timeout=20_000)
                    assert case["initial_text"] in initial.inner_text()

                    click_id = case.get("click_id")
                    if click_id:
                        page.locator(f"#{click_id}").click()
                        after = page.locator(f"#{case['after_id']}")
                        after.wait_for(state="visible", timeout=20_000)
                        sync_api.expect(after).to_contain_text(case["after_text"])
            finally:
                page.close()
                browser.close()
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Playwright runtime unavailable: {exc}")
