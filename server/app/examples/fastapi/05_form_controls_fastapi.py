from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from pywasm_ui import (
    ButtonWidget,
    CallbackResponse,
    CardWidget,
    CheckboxWidget,
    DatePickerWidget,
    EventPayload,
    HeadingWidget,
    LabelWidget,
    ModalWidget,
    OptionWidget,
    ProgressWidget,
    PyWasmSession,
    SelectWidget,
    StackWidget,
    Style,
    WasmWidget,
    WindowWidget,
    pywasm_ui,
)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CLIENT_ROOT = PROJECT_ROOT / "client"


def on_date_change(session: PyWasmSession, event: EventPayload) -> CallbackResponse:
    return session.update("date_value", text=f"Date: {event.value or '-'}")


def on_checkbox_change(session: PyWasmSession, _event: EventPayload) -> CallbackResponse:
    accepted = not bool(session.data.get("accepted", False))
    session.data["accepted"] = accepted
    return session.update("checkbox_value", text=f"Accepted: {accepted}")


def on_select_change(session: PyWasmSession, _event: EventPayload) -> CallbackResponse:
    count = int(session.data.get("select_changes", 0)) + 1
    session.data["select_changes"] = count
    return session.update("select_value", text=f"Select changed: {count}")


def on_progress_click(session: PyWasmSession) -> CallbackResponse:
    current = int(session.data.get("progress", 25))
    next_value = min(current + 15, 100)
    session.data["progress"] = next_value
    return session.update(
        "task_progress",
        attrs={"value": str(next_value), "max": "100"},
    )


def on_modal_toggle(session: PyWasmSession) -> CallbackResponse:
    is_open = not bool(session.data.get("modal_open", False))
    session.data["modal_open"] = is_open
    if is_open:
        return session.update("info_modal", attrs={"open": "true"})
    return session.update("info_modal", remove_attrs=["open"])


def _build_widgets() -> list[WasmWidget]:
    date_input = DatePickerWidget(
        id="date_input",
        parent="form_stack",
        value="2026-03-08",
        on_change=on_date_change,
    )
    agree_checkbox = CheckboxWidget(
        id="agree_checkbox",
        parent="form_stack",
        checked=False,
        on_change=on_checkbox_change,
    )
    category_select = SelectWidget(
        id="category_select",
        parent="form_stack",
        on_change=on_select_change,
    )

    progress_button = ButtonWidget(
        id="progress_btn",
        parent="form_stack",
        text="Increase Progress",
        on_click=on_progress_click,
    )
    modal_button = ButtonWidget(
        id="modal_btn",
        parent="form_stack",
        text="Toggle Modal",
        on_click=on_modal_toggle,
    )

    return [
        WindowWidget(id="window_main", parent="root", style=Style(max_width="720px", margin="0 auto")),
        CardWidget(
            id="card_main",
            parent="window_main",
            style=Style(padding="16px", border="1px solid #dbe2ea", border_radius="12px"),
        ),
        StackWidget(id="form_stack", parent="card_main", gap="10px"),
        HeadingWidget(id="form_title", parent="form_stack", text="Form Controls", level=2),
        date_input,
        LabelWidget(id="date_value", parent="form_stack", text="Date: 2026-03-08"),
        agree_checkbox,
        LabelWidget(id="checkbox_value", parent="form_stack", text="Accepted: False"),
        category_select,
        OptionWidget(id="category_alpha", parent="category_select", text="Alpha", value="alpha", selected=True),
        OptionWidget(id="category_beta", parent="category_select", text="Beta", value="beta"),
        LabelWidget(id="select_value", parent="form_stack", text="Select changed: 0"),
        ProgressWidget(id="task_progress", parent="form_stack", value=25, max_value=100),
        progress_button,
        modal_button,
        ModalWidget(
            id="info_modal",
            parent="form_stack",
            text="Server-driven modal content",
            is_open=False,
            style=Style(border="1px solid #94a3b8", padding="12px"),
        ),
    ]


def create_app() -> FastAPI:
    application = FastAPI(title="pyWasm form-controls example")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=_build_widgets(),
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    pywasm_ui.fastapi.register_frontend_routes(application, CLIENT_ROOT)
    return application


app = create_app()
