from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from pywasm_ui import (
    ButtonWidget,
    LabelWidget,
    StyleTemplate,
    WasmWidget,
    pywasm_ui,
)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CLIENT_ROOT = PROJECT_ROOT / "client"
TEMPLATE_PATH = Path(__file__).resolve().parent / "shared_style_template.json"


def _load_shared_template() -> StyleTemplate:
    if TEMPLATE_PATH.exists():
        return StyleTemplate.load(TEMPLATE_PATH)

    template = (
        StyleTemplate()
        .set_kind("Label", "font-family: ui-sans-serif; font-size: 15px; color: #0f172a")
        .set_class("primary", "background-color: #0ea5e9; color: #ffffff; border-radius: 8px")
        .set_class("muted", {"color": "#64748b"})
    )
    template.save(TEMPLATE_PATH)
    return template


def _build_widgets() -> list[WasmWidget]:
    title = LabelWidget(
        id="title_label",
        parent="root",
        text="Shared template active",
    )
    subtitle = LabelWidget(
        id="subtitle_label",
        parent="root",
        text="This style comes from template",
    )
    subtitle.add_class("muted")

    button = ButtonWidget(id="save_btn", parent="root", text="Save")
    button.add_class("primary")

    return [title, subtitle, button]


def create_app() -> FastAPI:
    application = FastAPI(title="pyWasm example 04 - style template")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=_build_widgets(),
        style_template=_load_shared_template(),
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "example": "04_style_template"}

    pywasm_ui.fastapi.register_frontend_routes(application, CLIENT_ROOT)
    return application


app = create_app()
