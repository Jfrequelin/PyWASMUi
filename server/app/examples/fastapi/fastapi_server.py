from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from pywasm_ui import (
    ButtonWidget,
    LabelWidget,
    PyWasmSession,
    Style,
    WasmWidget,
    merge_patches,
    patch_attrs,
    patch_style,
    pywasm_ui,
    set_text,
)
from pywasm_ui.protocol import EventPayload

PROJECT_ROOT = Path(__file__).resolve().parents[4]
USER_WEB_ROOT = PROJECT_ROOT / "server" / "app" / "examples" / "web"


def _increment_counter(
    session: PyWasmSession,
    *,
    state_key: str,
    label_id: str,
    step: int,
) -> dict[str, Any]:
    count = int(session.data.get(state_key, 0)) + step
    session.data[state_key] = count
    return merge_patches(
        label_id,
        set_text(label_id, str(count)),
        patch_attrs(label_id, {"data-clicks": count}),
        patch_style(label_id, Style(color="#0f172a", font_weight="700")),
    )


def _on_increment_1(session: PyWasmSession, _event: EventPayload) -> dict[str, Any]:
    return _increment_counter(session, state_key="label1_value", label_id="label1", step=1)


def _on_increment_2(session: PyWasmSession, _event: EventPayload) -> dict[str, Any]:
    return _increment_counter(session, state_key="label2_value", label_id="label2", step=2)


def _build_initial_widgets() -> list[WasmWidget]:
    label_style = Style(font_size="20px", color="#1f2937")
    button_style_1 = Style(background_color="#0ea5e9", border="none", padding="10px 16px")
    button_style_2 = Style(background_color="#14b8a6", border="none", padding="10px 16px")

    return [
        LabelWidget(id="label1", parent="root", text="0", style=label_style),
        ButtonWidget(
            id="btn1",
            parent="root",
            text="+1",
            enabled=True,
            classes=["primary"],
            on_click=_on_increment_1,
            style=button_style_1,
        ),
        LabelWidget(id="label2", parent="root", text="0", style=label_style),
        ButtonWidget(
            id="btn2",
            parent="root",
            text="+2",
            enabled=True,
            classes=["secondary"],
            on_click=_on_increment_2,
            style=button_style_2,
        ),
    ]


def create_app() -> FastAPI:
    application = FastAPI(title="pyWasm server")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=_build_initial_widgets(),
    )
    pywasm_ui.fastapi.register_packaged_assets(application, route_prefix="/pywasm-assets")

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    pywasm_ui.fastapi.register_frontend_routes(
        application,
        USER_WEB_ROOT,
        pages={
            "/playground": "index.html",
        },
        reserved_paths=("ws", "health", "pywasm-assets"),
    )
    return application


app = create_app()
