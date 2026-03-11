import os
from pathlib import Path

from fastapi import FastAPI

from pywasm_ui import (
    ButtonWidget,
    LabelWidget,
    PyWasmSession,
    WasmWidget,
    patch_style,
    pywasm_ui,
)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
WEB_ROOT = PROJECT_ROOT / "server" / "app" / "examples" / "web"


def _on_toggle_style(session: PyWasmSession):
    is_on = bool(session.data.get("is_on", False))
    next_value = not is_on
    session.data["is_on"] = next_value

    if next_value:
        return [
            {"id": "status_label", "text": "Theme: Active"},
            patch_style(
                "status_label",
                "color: #0f766e; background-color: #dcfce7",
                font_weight=700,
                padding="6px 10px",
            ),
        ]

    return [
        {"id": "status_label", "text": "Theme: Inactive"},
        patch_style(
            "status_label",
            "color: #334155; background-color: #e2e8f0",
            font_weight=400,
            padding="6px 10px",
        ),
    ]


def _build_widgets() -> list[WasmWidget]:
    status = LabelWidget(id="status_label", parent="root", text="Theme: Inactive")
    status.css("color: #334155; background-color: #e2e8f0", padding="6px 10px")

    toggle = ButtonWidget(id="toggle_btn", parent="root", text="Toggle style")
    toggle.add_class("primary")
    toggle.command(_on_toggle_style)
    return [status, toggle]


def create_app() -> FastAPI:
    application = FastAPI(title="PyWASMui example 03 - style updates")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=_build_widgets(),
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "example": "03_style_updates"}

    pywasm_ui.fastapi.register_packaged_assets(application, route_prefix="/pywasm-assets")
    pywasm_ui.fastapi.register_frontend_routes(
        application,
        WEB_ROOT,
        pages={"/": "index.html"},
        reserved_paths=("ws", "health", "pywasm-assets"),
    )
    return application


app = create_app()
