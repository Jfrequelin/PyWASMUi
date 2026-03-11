import os
from pathlib import Path

from fastapi import FastAPI

from pywasm_ui import CallbackResponse, ButtonWidget, LabelWidget, PyWasmSession, pywasm_ui

PROJECT_ROOT = Path(__file__).resolve().parents[4]
WEB_ROOT = PROJECT_ROOT / "server" / "app" / "examples" / "web"


def _on_add_widget(session: PyWasmSession) -> list[CallbackResponse]:
    next_index = int(session.data.get("dynamic_widget_count", 0)) + 1
    session.data["dynamic_widget_count"] = next_index

    dynamic_label = LabelWidget(
        id=f"dynamic_label_{next_index}",
        parent="root",
        text=f"Dynamic widget #{next_index}",
    )
    return [
        session.create(dynamic_label),
        session.update("add_widget_btn", text=f"Add another ({next_index})"),
    ]


def create_app() -> FastAPI:
    application = FastAPI(title="PyWASMui example 01 - single widget")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=[
            LabelWidget(id="hello_label", parent="root", text="Hello from PyWASMui"),
            ButtonWidget(id="add_widget_btn", parent="root", text="Add dynamic widget"),
        ],
        configure_session=lambda session: session.on_click("add_widget_btn", _on_add_widget),
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "example": "01_single_widget"}

    pywasm_ui.fastapi.register_packaged_assets(application, route_prefix="/pywasm-assets")
    pywasm_ui.fastapi.register_frontend_routes(
        application,
        WEB_ROOT,
        pages={"/": "index.html"},
        reserved_paths=("ws", "health", "pywasm-assets"),
    )
    return application


app = create_app()
