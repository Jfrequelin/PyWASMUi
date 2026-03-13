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

WIDGET_CASES = [
    {
        "name": "AlertWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "alert_status",
        "tag": "div",
    },
    {
        "name": "BadgeWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "badge_state",
        "tag": "span",
    },
    {
        "name": "ButtonWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "btn_1",
        "tag": "button",
        "action": "button_increment",
    },
    {
        "name": "CardWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "card_main",
        "tag": "div",
    },
    {
        "name": "CheckboxWidget",
        "target": "server.app.examples.fastapi:example_05_app",
        "check_id": "agree_checkbox",
        "tag": "input",
        "action": "checkbox_toggle",
    },
    {
        "name": "ContainerWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "list_item_1",
        "tag": "div",
    },
    {
        "name": "DatePickerWidget",
        "target": "server.app.examples.fastapi:example_05_app",
        "check_id": "date_input",
        "tag": "input",
        "action": "date_change",
    },
    {
        "name": "DividerWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "divider_top",
        "tag": "hr",
    },
    {
        "name": "HeadingWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "heading_title",
        "tag": "h2",
    },
    {
        "name": "IconButtonWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "btn_icon",
        "tag": "button",
        "action": "icon_notify",
    },
    {
        "name": "LabelWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "label_count_1",
        "tag": "p",
    },
    {
        "name": "ListViewWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "list_features",
        "tag": "div",
    },
    {
        "name": "ModalWidget",
        "target": "server.app.examples.fastapi:example_05_app",
        "check_id": "info_modal",
        "tag": "dialog",
        "action": "modal_toggle",
    },
    {
        "name": "OptionWidget",
        "target": "server.app.examples.fastapi:example_05_app",
        "check_id": "category_beta",
        "tag": "option",
        "action": "option_select",
    },
    {
        "name": "ParagraphWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "paragraph_intro",
        "tag": "p",
    },
    {
        "name": "ProgressWidget",
        "target": "server.app.examples.fastapi:example_05_app",
        "check_id": "task_progress",
        "tag": "progress",
        "action": "progress_increment",
    },
    {
        "name": "RowWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "row_actions",
        "tag": "div",
    },
    {
        "name": "SelectWidget",
        "target": "server.app.examples.fastapi:example_05_app",
        "check_id": "category_select",
        "tag": "select",
        "action": "select_change",
    },
    {
        "name": "SliderWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "slider_volume",
        "tag": "input",
        "action": "slider_change",
    },
    {
        "name": "StackWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "stack_main",
        "tag": "div",
    },
    {
        "name": "TextAreaWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "textarea_notes",
        "tag": "textarea",
        "action": "textarea_change",
    },
    {
        "name": "TextInputWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "input_name",
        "tag": "input",
        "action": "textinput_change",
    },
    {
        "name": "WindowWidget",
        "target": "server.app.examples.fastapi:all_widgets_app",
        "check_id": "window_main",
        "tag": "div",
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
def _live_fastapi_server(target: str) -> Iterator[str]:
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
        target,
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
                pytest.fail(f"Example server exited early: {target}")
            try:
                with urllib.request.urlopen(health_url, timeout=1) as response:
                    if response.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.2)
        else:
            process.terminate()
            process.wait(timeout=5)
            pytest.fail(f"Timed out waiting for health endpoint: {target}")

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


def _apply_widget_action(case: dict[str, str], chrome_driver, by, wait, ec) -> None:
    action = case.get("action")
    if not action:
        return

    click_intercepted = pytest.importorskip("selenium.common.exceptions").ElementClickInterceptedException

    def _click_with_fallback(element_id: str) -> None:
        element = wait.until(ec.element_to_be_clickable((by.ID, element_id)))
        chrome_driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center'});",
            element,
        )
        try:
            element.click()
        except click_intercepted:
            chrome_driver.execute_script("arguments[0].click();", element)

    def _counter_at_least(text: str, prefix: str, minimum: int) -> bool:
        if not text.startswith(prefix):
            return False
        try:
            value = int(text.split(":", 1)[1].strip())
        except (IndexError, ValueError):
            return False
        return value >= minimum

    if action == "button_increment":
        _click_with_fallback("btn_1")
        wait.until(lambda driver: "Count A: 1" in driver.find_element(by.ID, "label_count_1").text)
        return

    if action == "checkbox_toggle":
        checkbox = wait.until(ec.element_to_be_clickable((by.ID, "agree_checkbox")))
        checkbox.click()
        status = wait.until(ec.presence_of_element_located((by.ID, "checkbox_value")))
        wait.until(lambda _driver: "Accepted: True" in status.text)
        return

    if action == "date_change":
        date_input = wait.until(ec.presence_of_element_located((by.ID, "date_input")))
        chrome_driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            date_input,
            "2026-03-09",
        )
        status = wait.until(ec.presence_of_element_located((by.ID, "date_value")))
        wait.until(lambda _driver: "2026-03-09" in status.text)
        return

    if action == "icon_notify":
        _click_with_fallback("btn_icon")
        wait.until(
            lambda driver: "Icon button clicked" in driver.find_element(by.ID, "alert_status").text
        )
        return

    if action == "modal_toggle":
        _click_with_fallback("modal_btn")
        modal = wait.until(ec.presence_of_element_located((by.ID, "info_modal")))
        wait.until(lambda _driver: modal.get_attribute("open") in {"true", ""})
        return

    if action == "option_select":
        select = pytest.importorskip("selenium.webdriver.support.select").Select(
            wait.until(ec.presence_of_element_located((by.ID, "category_select")))
        )
        select.select_by_value("beta")
        option = wait.until(ec.presence_of_element_located((by.ID, "category_beta")))
        wait.until(lambda _driver: option.is_selected())
        return

    if action == "progress_increment":
        _click_with_fallback("progress_btn")
        progress = wait.until(ec.presence_of_element_located((by.ID, "task_progress")))
        wait.until(lambda _driver: progress.get_attribute("value") == "40")
        return

    if action == "select_change":
        select = pytest.importorskip("selenium.webdriver.support.select").Select(
            wait.until(ec.presence_of_element_located((by.ID, "category_select")))
        )
        select.select_by_value("beta")
        chrome_driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            select._el,
        )
        wait.until(
            lambda driver: _counter_at_least(
                driver.find_element(by.ID, "select_value").text,
                "Select changed:",
                1,
            )
        )
        return

    if action == "slider_change":
        slider = wait.until(ec.presence_of_element_located((by.ID, "slider_volume")))
        chrome_driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            slider,
            "35",
        )
        wait.until(
            lambda driver: "Slider value: 35" in driver.find_element(by.ID, "paragraph_slider").text
        )
        return

    if action == "textarea_change":
        textarea = wait.until(ec.presence_of_element_located((by.ID, "textarea_notes")))
        textarea.clear()
        textarea.send_keys("selenium notes")
        textarea.send_keys("\t")
        wait.until(
            lambda driver: "selenium notes" in driver.find_element(by.ID, "paragraph_notes").text
        )
        return

    if action == "textinput_change":
        text_input = wait.until(ec.presence_of_element_located((by.ID, "input_name")))
        text_input.clear()
        text_input.send_keys("Ada")
        text_input.send_keys("\t")
        wait.until(
            lambda driver: "Name preview: Ada" in driver.find_element(by.ID, "paragraph_name").text
        )
        return

    pytest.fail(f"Unknown action: {action}")


@pytest.mark.parametrize("case", WIDGET_CASES, ids=[c["name"] for c in WIDGET_CASES])
def test_each_widget_with_selenium(case: dict[str, str], chrome_driver) -> None:
    by = pytest.importorskip("selenium.webdriver.common.by").By
    wait = pytest.importorskip("selenium.webdriver.support.ui").WebDriverWait(chrome_driver, 20)
    ec = pytest.importorskip("selenium.webdriver.support.expected_conditions")

    with _live_fastapi_server(case["target"]) as live_server:
        chrome_driver.get(live_server)

        element = wait.until(ec.presence_of_element_located((by.ID, case["check_id"])))
        assert element.tag_name == case["tag"]

        _apply_widget_action(case, chrome_driver, by, wait, ec)
