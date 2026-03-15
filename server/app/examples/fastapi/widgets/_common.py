from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from pywasm_ui import DividerWidget, HeadingWidget, ParagraphWidget, Style, WasmWidget, pywasm_ui

PROJECT_ROOT = Path(__file__).resolve().parents[5]
USER_WEB_ROOT = PROJECT_ROOT / "server" / "app" / "examples" / "web"


def create_widget_example_app(*, title: str, description: str, widgets: list[WasmWidget]) -> FastAPI:
    app = FastAPI(title=f"PyWASMui Widget Example - {title}")

    initial_widgets: list[WasmWidget] = [
        HeadingWidget(
            id="example_title",
            parent="root",
            text=title,
            level=2,
            style=Style(margin_bottom="6px"),
        ),
        ParagraphWidget(
            id="example_description",
            parent="root",
            text=description,
            style=Style(color="#475569", margin_bottom="4px"),
        ),
        DividerWidget(id="example_divider", parent="root"),
    ]
    initial_widgets.extend(widgets)

    pywasm_ui.fastapi.bootstrap_app(
        app,
        USER_WEB_ROOT,
        ws_path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=initial_widgets,
        pages={"/playground": "index.html"},
        health_payload={"status": "ok"},
    )
    return app
