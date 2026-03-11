import os
from pathlib import Path

from fastapi import FastAPI

from pywasm_ui import (
    ButtonWidget,
    CardWidget,
    LabelWidget,
    PyWasmSession,
    RowWidget,
    StackWidget,
    WasmWidget,
    WindowWidget,
    pywasm_ui,
)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
WEB_ROOT = PROJECT_ROOT / "server" / "app" / "examples" / "web"


def _on_increment(session: PyWasmSession) -> dict[str, str]:
    current = int(session.data.get("count", 0)) + 1
    session.data["count"] = current
    return {"id": "counter_label", "text": f"Count: {current}"}


def _build_widgets() -> list[WasmWidget]:
    increment_button = ButtonWidget(id="increment_btn", parent="controls_row", text="+1")
    increment_button.command(_on_increment)

    return [
        WindowWidget(id="window_main", parent="root"),
        CardWidget(id="card_main", parent="window_main"),
        StackWidget(id="content_stack", parent="card_main", gap="10px"),
        LabelWidget(id="title_label", parent="content_stack", text="Composition with parent/child"),
        RowWidget(id="controls_row", parent="content_stack", gap="10px"),
        LabelWidget(id="counter_label", parent="controls_row", text="Count: 0"),
        increment_button,
    ]


def create_app() -> FastAPI:
    application = FastAPI(title="PyWASMui example 02 - composition")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=_build_widgets(),
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "example": "02_widget_composition"}

    pywasm_ui.fastapi.register_packaged_assets(application, route_prefix="/pywasm-assets")
    pywasm_ui.fastapi.register_frontend_routes(
        application,
        WEB_ROOT,
        pages={"/": "index.html"},
        reserved_paths=("ws", "health", "pywasm-assets"),
    )
    return application


app = create_app()
