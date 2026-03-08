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
def _live_example_server() -> Iterator[str]:
    root = Path(__file__).resolve().parents[2]

    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        port = int(sock.getsockname()[1])

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{root / 'python_lib'}:{env.get('PYTHONPATH', '')}".rstrip(":")
    command = [
        PYTHON,
        "-m",
        "uvicorn",
        "server.app.examples.fastapi:example_05_app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
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
                pytest.fail("Example server exited early for new widgets test")
            try:
                with urllib.request.urlopen(health_url, timeout=1) as response:
                    if response.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.2)
        else:
            process.terminate()
            process.wait(timeout=5)
            pytest.fail("Timed out waiting for health endpoint")

        try:
            yield base_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


@pytest.fixture
def chrome_driver() -> Iterator[object]:
    webdriver = pytest.importorskip("selenium.webdriver")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Selenium Chrome driver is unavailable: {exc}")

    try:
        yield driver
    finally:
        driver.quit()


def test_new_widgets_interactions_with_selenium(chrome_driver) -> None:
    by = pytest.importorskip("selenium.webdriver.common.by").By
    select_helper = pytest.importorskip("selenium.webdriver.support.select").Select
    wait = pytest.importorskip("selenium.webdriver.support.ui").WebDriverWait(chrome_driver, 20)
    ec = pytest.importorskip("selenium.webdriver.support.expected_conditions")

    with _live_example_server() as live_server:
        chrome_driver.get(live_server)

        title = wait.until(ec.presence_of_element_located((by.ID, "form_title")))
        assert "Form Controls" in title.text

        date_input = wait.until(ec.presence_of_element_located((by.ID, "date_input")))
        chrome_driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            date_input,
            "2026-03-09",
        )

        date_value = wait.until(ec.presence_of_element_located((by.ID, "date_value")))
        wait.until(lambda _driver: "2026-03-09" in date_value.text)

        checkbox = wait.until(ec.element_to_be_clickable((by.ID, "agree_checkbox")))
        checkbox.click()

        checkbox_value = wait.until(ec.presence_of_element_located((by.ID, "checkbox_value")))
        wait.until(lambda _driver: "Accepted: True" in checkbox_value.text)

        select_el = wait.until(ec.presence_of_element_located((by.ID, "category_select")))
        select_helper(select_el).select_by_value("beta")

        select_value = wait.until(ec.presence_of_element_located((by.ID, "select_value")))
        wait.until(lambda _driver: "Select changed: 1" in select_value.text)

        progress_button = wait.until(ec.element_to_be_clickable((by.ID, "progress_btn")))
        progress_button.click()

        progress = wait.until(ec.presence_of_element_located((by.ID, "task_progress")))
        wait.until(lambda _driver: progress.get_attribute("value") == "40")

        modal_button = wait.until(ec.element_to_be_clickable((by.ID, "modal_btn")))
        modal_button.click()

        modal = wait.until(ec.presence_of_element_located((by.ID, "info_modal")))
        wait.until(lambda _driver: modal.get_attribute("open") in {"true", ""})
