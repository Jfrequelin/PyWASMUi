from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from pywasm_ui import (
    AlertWidget,
    BadgeWidget,
    ButtonWidget,
    CardWidget,
    ConnectionStatusWidget,
    ContainerWidget,
    DividerWidget,
    HeadingWidget,
    IconButtonWidget,
    LabelWidget,
    ListViewWidget,
    ParagraphWidget,
    PyWasmSession,
    RowWidget,
    SliderWidget,
    StackWidget,
    Style,
    TextAreaWidget,
    TextInputWidget,
    WasmWidget,
    WindowWidget,
    pywasm_ui,
)
from pywasm_ui.protocol import EventPayload
from pywasm_ui.session.types import CallbackResponse

PROJECT_ROOT = Path(__file__).resolve().parents[4]
CLIENT_ROOT = PROJECT_ROOT / "client"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _on_delete_row(row_id: str):
    def _handler(session: PyWasmSession) -> list[CallbackResponse]:
        return [
            session.delete(row_id),
            session.update("badge_state", text=f"Deleted {row_id}"),
        ]

    return _handler


def _build_table_row_widgets(row_id: str, parent: str, text: str) -> list[WasmWidget]:
    delete_button = ButtonWidget(
        id=f"{row_id}_delete",
        parent=row_id,
        text="Supprimer",
        style=Style(background_color="#ef4444", color="#ffffff", border="none"),
    )
    delete_button.command(_on_delete_row(row_id))

    return [
        RowWidget(
            id=row_id,
            parent=parent,
            gap="10px",
            style=Style(justify_content="space-between", border_bottom="1px solid #e2e8f0"),
        ),
        LabelWidget(id=f"{row_id}_label", parent=row_id, text=text),
        delete_button,
    ]


def _update_counter(
    session: PyWasmSession,
    *,
    state_key: str,
    label_id: str,
    prefix: str,
    step: int,
    action_label: str,
) -> list[CallbackResponse]:
    count = _safe_int(session.data.get(state_key), default=0) + step
    session.data[state_key] = count

    label = session.widget(label_id)
    if label is not None:
        label.text(f"{prefix}: {count}")

    return [
        session.update(label_id, text=f"{prefix}: {count}"),
        session.update("badge_state", text=f"Last action: {action_label}"),
    ]


def on_add_row_click(session: PyWasmSession) -> list[CallbackResponse]:
    next_id = _safe_int(session.data.get("table_next_row_id"), default=3)
    session.data["table_next_row_id"] = next_id + 1
    row_id = f"table_row_{next_id}"
    row_widgets = _build_table_row_widgets(row_id, "table_rows", f"Ligne {next_id}")

    responses: list[CallbackResponse] = [
        session.update("badge_state", text=f"Added {row_id}"),
    ]
    responses.extend(session.create(widget) for widget in row_widgets)
    return responses


def on_btn1_click(session: PyWasmSession) -> list[CallbackResponse]:
    return _update_counter(
        session,
        state_key="count_1",
        label_id="label_count_1",
        prefix="Count A",
        step=1,
        action_label="+1",
    )


def on_btn2_click(session: PyWasmSession) -> list[CallbackResponse]:
    return _update_counter(
        session,
        state_key="count_2",
        label_id="label_count_2",
        prefix="Count B",
        step=2,
        action_label="+2",
    )


def on_icon_click(session: PyWasmSession) -> list[CallbackResponse]:
    note_count = _safe_int(session.data.get("icon_note_count"), default=0) + 1
    session.data["icon_note_count"] = note_count

    note_widget = LabelWidget(
        id=f"icon_note_{note_count}",
        parent="stack_main",
        text=f"Dynamic note created on click #{note_count}",
        style=Style(color="#475569", font_size="13px"),
    )

    alert = session.widget("alert_status")
    if alert is not None:
        alert.text("Icon button clicked")
        alert.style.background_color = "#dcfce7"
        alert.style.color = "#14532d"

    return [
        session.update(
            "alert_status",
            text="Icon button clicked",
            style={"background-color": "#dcfce7", "color": "#14532d"},
        ),
        session.create(note_widget),
    ]


def on_name_change(session: PyWasmSession, event: EventPayload) -> CallbackResponse:
    name = str(event.value or "")
    return session.update("paragraph_name", text=f"Name preview: {name}")


def on_slider_change(session: PyWasmSession, event: EventPayload) -> CallbackResponse:
    value = _safe_int(event.value, default=0)
    return session.update("paragraph_slider", text=f"Slider value: {value}")


def on_notes_change(session: PyWasmSession, event: EventPayload) -> CallbackResponse:
    notes = str(event.value or "")
    preview = notes if len(notes) <= 80 else f"{notes[:77]}..."
    return session.update("paragraph_notes", text=f"Notes preview: {preview}")


def _build_interactive_widgets() -> dict[str, WasmWidget]:
    name_input = TextInputWidget(id="input_name", parent="stack_main", value="")
    name_input.on_change(on_name_change)

    btn_1 = ButtonWidget(id="btn_1", parent="row_actions", text="+1")
    btn_1.command(on_btn1_click)

    btn_2 = ButtonWidget(id="btn_2", parent="row_actions", text="+2")
    btn_2.command(on_btn2_click)

    btn_icon = IconButtonWidget(id="btn_icon", parent="row_actions", icon="*", text="Notify")
    btn_icon.command(on_icon_click)

    slider_volume = SliderWidget(
        id="slider_volume",
        parent="stack_main",
        value=20,
        min_value=0,
        max_value=100,
        step=5,
    )
    slider_volume.on_change(on_slider_change)

    textarea_notes = TextAreaWidget(
        id="textarea_notes",
        parent="stack_main",
        value="",
        style=Style(min_height="90px"),
    )
    textarea_notes.on_change(on_notes_change)

    btn_add_row = ButtonWidget(
        id="btn_add_row",
        parent="stack_main",
        text="Ajouter une ligne",
        style=Style(background_color="#0f766e", color="#ffffff", border="none"),
    )
    btn_add_row.command(on_add_row_click)

    return {
        "name_input": name_input,
        "btn_1": btn_1,
        "btn_2": btn_2,
        "btn_icon": btn_icon,
        "slider_volume": slider_volume,
        "textarea_notes": textarea_notes,
        "btn_add_row": btn_add_row,
    }


def _build_initial_widgets() -> list[WasmWidget]:
    widgets = _build_interactive_widgets()
    return [
        ConnectionStatusWidget(id="conn_status", parent="root", state="connecting"),
        WindowWidget(
            id="window_main",
            parent="root",
            style=Style(max_width="960px", margin="0 auto"),
        ),
        CardWidget(
            id="card_main",
            parent="window_main",
            style=Style(padding="16px", border="1px solid #dbe2ea", border_radius="12px"),
        ),
        StackWidget(id="stack_main", parent="card_main", gap="12px"),
        HeadingWidget(id="heading_title", parent="stack_main", text="Widget Showcase", level=2),
        ParagraphWidget(
            id="paragraph_intro",
            parent="stack_main",
            text="Demo with a full set of framework-like widgets.",
        ),
        DividerWidget(id="divider_top", parent="stack_main"),
        RowWidget(id="row_actions", parent="stack_main", gap="10px"),
        BadgeWidget(id="badge_state", parent="row_actions", text="Ready", variant="info"),
        LabelWidget(id="label_count_1", parent="row_actions", text="Count A: 0"),
        widgets["btn_1"],
        LabelWidget(id="label_count_2", parent="row_actions", text="Count B: 0"),
        widgets["btn_2"],
        widgets["btn_icon"],
        AlertWidget(id="alert_status", parent="stack_main", text="No alert", level="info"),
        widgets["name_input"],
        ParagraphWidget(id="paragraph_name", parent="stack_main", text="Name preview:"),
        widgets["slider_volume"],
        ParagraphWidget(id="paragraph_slider", parent="stack_main", text="Slider value: 20"),
        widgets["textarea_notes"],
        ParagraphWidget(id="paragraph_notes", parent="stack_main", text="Notes preview:"),
        ListViewWidget(
            id="list_features",
            parent="stack_main",
            style=Style(border="1px dashed #cbd5e1", padding="10px"),
        ),
        ContainerWidget(id="list_item_1", parent="list_features"),
        LabelWidget(id="list_item_1_text", parent="list_item_1", text="- Framework-like widgets"),
        ContainerWidget(id="list_item_2", parent="list_features"),
        LabelWidget(id="list_item_2_text", parent="list_item_2", text="- Python callbacks"),
        ContainerWidget(id="list_item_3", parent="list_features"),
        LabelWidget(id="list_item_3_text", parent="list_item_3", text="- WS pending/ack flow"),
        DividerWidget(id="divider_table", parent="stack_main"),
        HeadingWidget(id="heading_table", parent="stack_main", text="Tableau dynamique", level=3),
        ParagraphWidget(
            id="paragraph_table",
            parent="stack_main",
            text=(
                "Chaque ligne a un bouton Supprimer, et le bouton Ajouter une ligne "
                "est en dessous."
            ),
        ),
        ContainerWidget(
            id="table_rows",
            parent="stack_main",
            style=Style(border="1px solid #e2e8f0", border_radius="8px", padding="8px"),
        ),
        *_build_table_row_widgets("table_row_1", "table_rows", "Ligne 1"),
        *_build_table_row_widgets("table_row_2", "table_rows", "Ligne 2"),
        widgets["btn_add_row"],
    ]


def create_app() -> FastAPI:
    application = FastAPI(title="pyWasm all-widgets example")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=_build_initial_widgets(),
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    pywasm_ui.fastapi.register_frontend_routes(
        application,
        CLIENT_ROOT,
        pages={
            "/showcase": "index.html",
        },
    )
    return application


app = create_app()
