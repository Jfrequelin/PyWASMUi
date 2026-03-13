import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from pywasm_ui import (
    AlertWidget,
    BadgeWidget,
    ButtonWidget,
    CheckboxWidget,
    CardWidget,
    ConnectionStatusWidget,
    ContainerWidget,
    DatePickerWidget,
    DividerWidget,
    HeadingWidget,
    IconButtonWidget,
    LabelWidget,
    ListViewWidget,
    ModalWidget,
    OptionWidget,
    ParagraphWidget,
    ProgressWidget,
    PyWasmSession,
    RowWidget,
    SelectWidget,
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
USER_WEB_ROOT = PROJECT_ROOT / "server" / "app" / "examples" / "web"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(str(value))
    except (TypeError, ValueError):
        return default


@dataclass
class InteractiveWidgets:
    name_input: WasmWidget
    btn_1: WasmWidget
    btn_2: WasmWidget
    btn_icon: WasmWidget
    slider_volume: WasmWidget
    textarea_notes: WasmWidget
    btn_add_row: WasmWidget
    checkbox_terms: WasmWidget
    date_input: WasmWidget
    category_select: WasmWidget
    progress_btn: WasmWidget
    modal_btn: WasmWidget


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


def on_checkbox_change(session: PyWasmSession, _event: EventPayload) -> list[CallbackResponse]:
    accepted = not bool(session.data.get("accepted", False))
    session.data["accepted"] = accepted
    return [
        session.update("checkbox_value", text=f"Accepted: {accepted}"),
        session.update("badge_state", text="Checkbox toggled"),
    ]


def on_date_change(session: PyWasmSession, event: EventPayload) -> list[CallbackResponse]:
    value = str(event.value or "-")
    return [
        session.update("date_value", text=f"Date: {value}"),
        session.update("badge_state", text="Date changed"),
    ]


def on_select_change(session: PyWasmSession, _event: EventPayload) -> list[CallbackResponse]:
    count = _safe_int(session.data.get("select_changes"), default=0) + 1
    session.data["select_changes"] = count
    return [
        session.update("select_value", text=f"Select changed: {count}"),
        session.update("badge_state", text="Select changed"),
    ]


def on_progress_click(session: PyWasmSession) -> list[CallbackResponse]:
    current = _safe_int(session.data.get("progress"), default=25)
    next_value = min(current + 15, 100)
    session.data["progress"] = next_value
    return [
        session.update("task_progress", attrs={"value": str(next_value), "max": "100"}),
        session.update("badge_state", text="Progress increased"),
    ]


def on_modal_toggle(session: PyWasmSession) -> list[CallbackResponse]:
    is_open = not bool(session.data.get("modal_open", False))
    session.data["modal_open"] = is_open
    if is_open:
        return [
            session.update("info_modal", attrs={"open": "true"}),
            session.update("badge_state", text="Modal opened"),
        ]
    return [
        session.update("info_modal", remove_attrs=["open"]),
        session.update("badge_state", text="Modal closed"),
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


def _build_interactive_widgets() -> InteractiveWidgets:
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

    checkbox_terms = CheckboxWidget(
        id="checkbox_terms",
        parent="stack_main",
        checked=False,
        on_change=on_checkbox_change,
    )

    date_input = DatePickerWidget(
        id="date_input",
        parent="stack_main",
        value="2026-03-09",
        on_change=on_date_change,
    )

    category_select = SelectWidget(
        id="category_select",
        parent="stack_main",
        on_change=on_select_change,
    )

    progress_btn = ButtonWidget(
        id="progress_btn",
        parent="stack_main",
        text="Increase Progress",
        on_click=on_progress_click,
    )

    modal_btn = ButtonWidget(
        id="modal_btn",
        parent="modal_anchor",
        text="Toggle Modal",
        on_click=on_modal_toggle,
    )

    return InteractiveWidgets(
        name_input=name_input,
        btn_1=btn_1,
        btn_2=btn_2,
        btn_icon=btn_icon,
        slider_volume=slider_volume,
        textarea_notes=textarea_notes,
        btn_add_row=btn_add_row,
        checkbox_terms=checkbox_terms,
        date_input=date_input,
        category_select=category_select,
        progress_btn=progress_btn,
        modal_btn=modal_btn,
    )


def _build_showcase_header(widgets: InteractiveWidgets) -> list[WasmWidget]:
    return [
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
        widgets.btn_1,
        LabelWidget(id="label_count_2", parent="row_actions", text="Count B: 0"),
        widgets.btn_2,
        widgets.btn_icon,
        AlertWidget(id="alert_status", parent="stack_main", text="No alert", level="info"),
    ]


def _build_interaction_section(widgets: InteractiveWidgets) -> list[WasmWidget]:
    return [
        widgets.name_input,
        ParagraphWidget(id="paragraph_name", parent="stack_main", text="Name preview:"),
        widgets.slider_volume,
        ParagraphWidget(id="paragraph_slider", parent="stack_main", text="Slider value: 20"),
        widgets.textarea_notes,
        ParagraphWidget(id="paragraph_notes", parent="stack_main", text="Notes preview:"),
        widgets.checkbox_terms,
        LabelWidget(id="checkbox_value", parent="stack_main", text="Accepted: False"),
        widgets.date_input,
        LabelWidget(id="date_value", parent="stack_main", text="Date: 2026-03-09"),
        widgets.category_select,
        OptionWidget(
            id="category_alpha",
            parent="category_select",
            text="Alpha",
            value="alpha",
            selected=True,
        ),
        OptionWidget(id="category_beta", parent="category_select", text="Beta", value="beta"),
        LabelWidget(id="select_value", parent="stack_main", text="Select changed: 0"),
        ProgressWidget(id="task_progress", parent="stack_main", value=25, max_value=100),
        widgets.progress_btn,
        ContainerWidget(
            id="modal_anchor",
            parent="stack_main",
            style=Style(position="relative", display="inline-block"),
        ),
        widgets.modal_btn,
        ModalWidget(
            id="info_modal",
            parent="modal_anchor",
            text="Server-driven modal content",
            is_open=False,
            style=Style(
                border="1px solid #94a3b8",
                padding="12px",
                margin="0",
                position="absolute",
                top="calc(100% + 8px)",
                left="0",
                z_index="20",
            ),
        ),
    ]


def _build_features_section() -> list[WasmWidget]:
    return [
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
    ]


def _build_dynamic_table_section(widgets: InteractiveWidgets) -> list[WasmWidget]:
    return [
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
        widgets.btn_add_row,
    ]


def _build_initial_widgets(include_status_widget: bool = False) -> list[WasmWidget]:
    widgets = _build_interactive_widgets()
    initial_widgets = [
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
        *_build_showcase_header(widgets),
        *_build_interaction_section(widgets),
        *_build_features_section(),
        *_build_dynamic_table_section(widgets),
    ]
    if include_status_widget:
        initial_widgets.insert(0, ConnectionStatusWidget(id="conn_status", parent="root", state="connecting"))
    return initial_widgets


def create_app() -> FastAPI:
    application = FastAPI(title="PyWASMui all-widgets example")
    pywasm_ui.fastapi.register_websocket_endpoint(
        application,
        path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=_build_initial_widgets(
            include_status_widget=os.getenv("PYWASM_INCLUDE_STATUS_WIDGET") == "1"
        ),
    )
    pywasm_ui.fastapi.register_packaged_assets(application, route_prefix="/pywasm-assets")

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    pywasm_ui.fastapi.register_frontend_routes(
        application,
        USER_WEB_ROOT,
        pages={
            "/showcase": "index.html",
        },
        reserved_paths=("ws", "health", "pywasm-assets"),
    )
    return application


app = create_app()
