"""Example 10: full widget catalog showcase, implemented step by step."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from pywasm_ui import (
    AlertWidget,
    BadgeWidget,
    ButtonWidget,
    CardWidget,
    CheckboxWidget,
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
WEB_ROOT = PROJECT_ROOT / "server" / "app" / "examples" / "web"
THEMES_ROOT = WEB_ROOT / "themes"
DEFAULT_THEME = "modern"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _discover_theme_names() -> list[str]:
    preferred_order = ["modern", "slate", "sunset", "ladys", "neo-ember"]
    discovered = {
        path.stem
        for path in THEMES_ROOT.glob("*.css")
        if path.is_file() and path.stem != "base"
    }
    ordered = [name for name in preferred_order if name in discovered]
    extras = sorted(name for name in discovered if name not in preferred_order)
    names = ordered + extras
    return names or [DEFAULT_THEME]


def _theme_label(theme_name: str) -> str:
    return theme_name.replace("-", " ").title()


def _build_theme_options(theme_names: list[str]) -> list[OptionWidget]:
    active = DEFAULT_THEME if DEFAULT_THEME in theme_names else theme_names[0]
    return [
        OptionWidget(
            id=f"theme_option_{name.replace('-', '_')}",
            parent="theme_select",
            text=_theme_label(name),
            value=name,
            selected=name == active,
        )
        for name in theme_names
    ]


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
    theme_select: WasmWidget
    progress_btn: WasmWidget
    modal_btn: WasmWidget
    tooltip_target_btn: WasmWidget


# Step 1: handlers used by interactive widgets.
def _on_delete_row(row_id: str):
    def _handler(session: PyWasmSession) -> list[CallbackResponse]:
        return [
            session.delete(row_id),
            session.update("badge_state", text=f"Ligne supprimee: {row_id}"),
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
            style=Style(
                justify_content="space-between",
                border_bottom="1px solid #e2e8f0",
                padding_top="8px",
                padding_bottom="8px",
            ),
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
    return [
        session.update(label_id, text=f"{prefix}: {count}"),
        session.update("badge_state", text=f"Derniere action: {action_label}"),
    ]


def on_btn1_click(session: PyWasmSession) -> list[CallbackResponse]:
    return _update_counter(
        session,
        state_key="count_1",
        label_id="label_count_1",
        prefix="Compteur A",
        step=1,
        action_label="Increment du compteur A (+1)",
    )


def on_btn2_click(session: PyWasmSession) -> list[CallbackResponse]:
    return _update_counter(
        session,
        state_key="count_2",
        label_id="label_count_2",
        prefix="Compteur B",
        step=2,
        action_label="Increment du compteur B (+2)",
    )


def on_icon_click(session: PyWasmSession) -> list[CallbackResponse]:
    note_count = _safe_int(session.data.get("icon_note_count"), default=0) + 1
    session.data["icon_note_count"] = note_count
    note_widget = LabelWidget(
        id=f"icon_note_{note_count}",
        parent="stack_interactions",
        text=f"Note dynamique ajoutee apres clic ({note_count})",
        style=Style(color="#475569", font_size="13px"),
    )
    return [
        session.update(
            "alert_status",
            text="Le bouton d'action a ajoute une note explicative.",
            style={"background-color": "#dcfce7", "color": "#14532d"},
        ),
        session.create(note_widget),
    ]


def on_add_row_click(session: PyWasmSession) -> list[CallbackResponse]:
    next_id = _safe_int(session.data.get("table_next_row_id"), default=3)
    session.data["table_next_row_id"] = next_id + 1
    row_id = f"table_row_{next_id}"
    row_widgets = _build_table_row_widgets(row_id, "table_rows", f"Ligne dynamique {next_id}")
    responses: list[CallbackResponse] = [session.update("badge_state", text=f"Ligne ajoutee: {row_id}")]
    responses.extend(session.create(widget) for widget in row_widgets)
    return responses


def on_checkbox_change(session: PyWasmSession, _event: EventPayload) -> list[CallbackResponse]:
    accepted = not bool(session.data.get("accepted", False))
    session.data["accepted"] = accepted
    return [
        session.update("checkbox_value", text=f"Conditions acceptees: {accepted}"),
        session.update("badge_state", text="La case a cocher a ete modifiee."),
    ]


def on_date_change(session: PyWasmSession, event: EventPayload) -> list[CallbackResponse]:
    value = str(event.value or "-")
    return [
        session.update("date_value", text=f"Date selectionnee: {value}"),
        session.update("badge_state", text="La date a ete mise a jour."),
    ]


def on_select_change(session: PyWasmSession, _event: EventPayload) -> list[CallbackResponse]:
    count = _safe_int(session.data.get("select_changes"), default=0) + 1
    session.data["select_changes"] = count
    return [
        session.update("select_value", text=f"Categorie modifiee: {count} fois"),
        session.update("badge_state", text="La categorie a ete changee."),
    ]


def on_theme_change(session: PyWasmSession, event: EventPayload) -> list[CallbackResponse]:
    theme_name = str(event.value or "modern")
    session.data["theme_name"] = theme_name
    return [
        session.update("badge_state", text=f"Theme actif: {theme_name}"),
        session.update("theme_value", text=f"Theme actif: {theme_name}"),
    ]


def on_progress_click(session: PyWasmSession) -> list[CallbackResponse]:
    current = _safe_int(session.data.get("progress"), default=25)
    next_value = min(current + 15, 100)
    session.data["progress"] = next_value
    return [
        session.update("task_progress", attrs={"value": str(next_value), "max": "100"}),
        session.update("badge_state", text=f"Progression mise a jour: {next_value}%"),
    ]


def on_modal_toggle(session: PyWasmSession) -> list[CallbackResponse]:
    is_open = not bool(session.data.get("modal_open", False))
    session.data["modal_open"] = is_open
    if is_open:
        return [
            session.update("info_modal", attrs={"open": "true"}),
            session.update("badge_state", text="La modale d'information est ouverte."),
        ]
    return [
        session.update("info_modal", remove_attrs=["open"]),
        session.update("badge_state", text="La modale d'information est fermee."),
    ]


def on_name_change(session: PyWasmSession, event: EventPayload) -> CallbackResponse:
    name = str(event.value or "")
    return session.update("paragraph_name", text=f"Apercu du nom saisi: {name}")


def on_slider_change(session: PyWasmSession, event: EventPayload) -> CallbackResponse:
    value = _safe_int(event.value, default=0)
    return session.update("paragraph_slider", text=f"Valeur du curseur: {value}")


def on_notes_change(session: PyWasmSession, event: EventPayload) -> CallbackResponse:
    notes = str(event.value or "")
    preview = notes if len(notes) <= 80 else f"{notes[:77]}..."
    return session.update("paragraph_notes", text=f"Apercu de vos notes: {preview}")


# Step 2: widget builders for each section of the catalog page.
def _build_interactive_widgets() -> InteractiveWidgets:
    name_input = TextInputWidget(id="input_name", parent="stack_interactions", value="")
    name_input.on_change(on_name_change)

    btn_1 = ButtonWidget(id="btn_1", parent="row_actions", text="Ajouter +1")
    btn_1.command(on_btn1_click)
    btn_1.tooltip("Ajoute 1 au compteur A.")

    btn_2 = ButtonWidget(id="btn_2", parent="row_actions", text="Ajouter +2")
    btn_2.command(on_btn2_click)
    btn_2.tooltip("Ajoute 2 au compteur B.")

    btn_icon = IconButtonWidget(id="btn_icon", parent="row_actions", icon="*", text="Ajouter une note")
    btn_icon.command(on_icon_click)
    btn_icon.tooltip("Ajoute une note dynamique dans la section interactions.")

    slider_volume = SliderWidget(
        id="slider_volume",
        parent="stack_interactions",
        value=20,
        min_value=0,
        max_value=100,
        step=5,
    )
    slider_volume.on_change(on_slider_change)
    slider_volume.tooltip("Curseur numerique de 0 a 100 (pas de 5).")

    textarea_notes = TextAreaWidget(
        id="textarea_notes",
        parent="stack_interactions",
        value="",
        style=Style(min_height="90px"),
    )
    textarea_notes.on_change(on_notes_change)
    textarea_notes.tooltip("Zone de texte multilignes pour notes libres.")

    btn_add_row = ButtonWidget(
        id="btn_add_row",
        parent="stack_table",
        text="Ajouter une ligne",
        style=Style(background_color="#0f766e", color="#ffffff", border="none"),
    )
    btn_add_row.command(on_add_row_click)
    btn_add_row.tooltip("Ajoute une nouvelle ligne dans le tableau dynamique.")

    checkbox_terms = CheckboxWidget(
        id="checkbox_terms",
        parent="stack_interactions",
        checked=False,
        on_change=on_checkbox_change,
    )
    checkbox_terms.tooltip("Active ou desactive une option booleenne.")

    date_input = DatePickerWidget(
        id="date_input",
        parent="stack_interactions",
        value="2026-03-09",
        on_change=on_date_change,
    )
    date_input.tooltip("Selectionnez une date pour mettre a jour la valeur.")

    category_select = SelectWidget(
        id="category_select",
        parent="stack_interactions",
        on_change=on_select_change,
    )
    category_select.tooltip("Choisissez une categorie metier.")

    theme_select = SelectWidget(
            id="theme_select",
            parent="stack_interactions",
            on_change=on_theme_change,
    )
    theme_select.tooltip("Change le theme visuel global de la page.")

    progress_btn = ButtonWidget(
        id="progress_btn",
        parent="stack_interactions",
        text="Augmenter la progression",
        on_click=on_progress_click,
    )
    progress_btn.tooltip("Augmente la barre de progression de 15%.")

    modal_btn = ButtonWidget(
        id="modal_btn",
        parent="modal_anchor",
        text="Afficher / masquer l'aide",
        on_click=on_modal_toggle,
    )
    modal_btn.tooltip("Ouvre ou ferme la modale d'information.")

    tooltip_target_btn = ButtonWidget(
        id="tooltip_target_btn",
        parent="tooltip_anchor",
        text="Survolez-moi 2 secondes",
    )
    tooltip_target_btn.tooltip(
        "Astuce: vous utilisez une infobulle native du framework, ajoutable sur n'importe quel widget.",
        delay_ms=2000,
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
        theme_select=theme_select,
        progress_btn=progress_btn,
        modal_btn=modal_btn,
        tooltip_target_btn=tooltip_target_btn,
    )


def _build_showcase_header(widgets: InteractiveWidgets) -> list[WasmWidget]:
    return [
        HeadingWidget(id="heading_title", parent="stack_header", text="Catalogue interactif des widgets", level=2),
        ParagraphWidget(
            id="paragraph_intro",
            parent="stack_header",
            text="Cette page montre chaque widget disponible avec des exemples d'interactions en direct.",
        ),
        DividerWidget(id="divider_top", parent="stack_header"),
        RowWidget(id="row_actions", parent="stack_header", gap="10px"),
        BadgeWidget(id="badge_state", parent="row_actions", text="Pret", variant="info"),
        LabelWidget(id="label_count_1", parent="row_actions", text="Compteur A: 0"),
        widgets.btn_1,
        LabelWidget(id="label_count_2", parent="row_actions", text="Compteur B: 0"),
        widgets.btn_2,
        widgets.btn_icon,
        AlertWidget(id="alert_status", parent="stack_header", text="Aucune alerte pour le moment.", level="info"),
    ]


def _build_interaction_section(widgets: InteractiveWidgets, theme_names: list[str]) -> list[WasmWidget]:
    return [
        widgets.name_input,
        ParagraphWidget(id="paragraph_name", parent="stack_interactions", text="Apercu du nom saisi:"),
        widgets.slider_volume,
        ParagraphWidget(id="paragraph_slider", parent="stack_interactions", text="Valeur du curseur: 20"),
        widgets.textarea_notes,
        ParagraphWidget(id="paragraph_notes", parent="stack_interactions", text="Apercu de vos notes:"),
        widgets.checkbox_terms,
        LabelWidget(id="checkbox_value", parent="stack_interactions", text="Conditions acceptees: False"),
        widgets.date_input,
        LabelWidget(id="date_value", parent="stack_interactions", text="Date selectionnee: 2026-03-09"),
        widgets.category_select,
        OptionWidget(
            id="category_alpha",
            parent="category_select",
            text="Alpha",
            value="alpha",
            selected=True,
        ),
        OptionWidget(id="category_beta", parent="category_select", text="Beta", value="beta"),
        LabelWidget(id="select_value", parent="stack_interactions", text="Categorie modifiee: 0 fois"),
        widgets.theme_select,
        *_build_theme_options(theme_names),
        LabelWidget(
            id="theme_value",
            parent="stack_interactions",
            text=f"Theme actif: {DEFAULT_THEME if DEFAULT_THEME in theme_names else theme_names[0]}",
        ),
        ProgressWidget(id="task_progress", parent="stack_interactions", value=25, max_value=100),
        widgets.progress_btn,
        LabelWidget(
            id="label_tooltip_explain",
            parent="stack_interactions",
            text="Widget infobulle: apparait apres 2 secondes de survol (ou focus clavier).",
        ),
        ContainerWidget(
            id="tooltip_anchor",
            parent="stack_interactions",
            style=Style(position="relative", display="inline-flex", flex_direction="column", gap="6px"),
        ),
        widgets.tooltip_target_btn,
        ContainerWidget(
            id="modal_anchor",
            parent="stack_interactions",
            style=Style(position="relative", display="inline-block"),
        ),
        widgets.modal_btn,
        ModalWidget(
            id="info_modal",
            parent="modal_anchor",
            text=(
                "Cette modale presente un exemple d'information contextuelle.\n"
                "Utilisez-la pour afficher de l'aide, des details ou une confirmation."
            ),
            is_open=False,
            style=Style(
                border="1px solid #94a3b8",
                padding="12px",
                margin="0",
                position="absolute",
                top="calc(100% + 8px)",
                left="0",
                z_index="9999",
            ),
        ),
    ]


def _build_features_section() -> list[WasmWidget]:
    return [
        ListViewWidget(
            id="list_features",
            parent="stack_features",
            style=Style(border="1px dashed #cbd5e1", padding="10px"),
        ),
        ContainerWidget(id="list_item_1", parent="list_features"),
        LabelWidget(id="list_item_1_text", parent="list_item_1", text="- Les widgets sont declaratifs et faciles a composer."),
        ContainerWidget(id="list_item_2", parent="list_features"),
        LabelWidget(id="list_item_2_text", parent="list_item_2", text="- Les callbacks Python pilotent les interactions utilisateur."),
        ContainerWidget(id="list_item_3", parent="list_features"),
        LabelWidget(id="list_item_3_text", parent="list_item_3", text="- Le flux WebSocket synchronise les mises a jour en temps reel."),
    ]


def _build_dynamic_table_section(widgets: InteractiveWidgets) -> list[WasmWidget]:
    return [
        DividerWidget(id="divider_table", parent="stack_table"),
        HeadingWidget(id="heading_table", parent="stack_table", text="Tableau dynamique (ajout et suppression)", level=3),
        ParagraphWidget(
            id="paragraph_table",
            parent="stack_table",
            text=(
                "Chaque ligne peut etre supprimee individuellement. Utilisez le bouton "
                "ci-dessous pour ajouter une nouvelle ligne dynamiquement."
            ),
        ),
        LabelWidget(
            id="label_table_rows_explain",
            parent="stack_table",
            text="Widget Container + Row + Button: liste dynamique avec suppression ligne par ligne.",
        ),
        ContainerWidget(
            id="table_rows",
            parent="stack_table",
            style=Style(border="1px solid #e2e8f0", border_radius="8px", padding="8px"),
        ),
        *_build_table_row_widgets("table_row_1", "table_rows", "Ligne 1"),
        *_build_table_row_widgets("table_row_2", "table_rows", "Ligne 2"),
        LabelWidget(
            id="label_table_add_explain",
            parent="stack_table",
            text="Le bouton ci-dessous ajoute une nouvelle ligne avec son propre bouton de suppression.",
        ),
        widgets.btn_add_row,
    ]


# Step 3: assemble full initial widget tree.
def _build_initial_widgets(theme_names: list[str]) -> list[WasmWidget]:
    widgets = _build_interactive_widgets()
    return [
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
        CardWidget(
            id="card_header",
            parent="stack_main",
            style=Style(padding="22px"),
        ),
        StackWidget(id="stack_header", parent="card_header", gap="10px"),
        CardWidget(
            id="card_interactions",
            parent="stack_main",
            style=Style(
                padding="22px",
                position="relative",
                overflow="visible",
                z_index="30",
            ),
        ),
        StackWidget(id="stack_interactions", parent="card_interactions", gap="10px"),
        CardWidget(
            id="card_features",
            parent="stack_main",
            style=Style(padding="22px"),
        ),
        StackWidget(id="stack_features", parent="card_features", gap="10px"),
        CardWidget(
            id="card_table",
            parent="stack_main",
            style=Style(padding="22px"),
        ),
        StackWidget(id="stack_table", parent="card_table", gap="10px"),
        *_build_showcase_header(widgets),
        *_build_interaction_section(widgets, theme_names),
        *_build_features_section(),
        *_build_dynamic_table_section(widgets),
    ]



# Step 4: create the FastAPI app and register websocket + frontend routes.
def create_app(include_status_widget: bool = False) -> FastAPI:
    application = FastAPI(title="PyWASMui example 10 - widget catalog")
    initial_widgets = _build_initial_widgets(_discover_theme_names())
    # Optional status widget: disabled by default to keep the template minimal.
    if include_status_widget:
        initial_widgets.insert(0, ConnectionStatusWidget(id="conn_status", parent="root", state="connecting"))

    pywasm_ui.fastapi.bootstrap_app(
        application,
        WEB_ROOT,
        ws_path="/ws",
        server_secret=os.getenv("PYWASM_SERVER_SECRET", "dev-server-secret-change-me"),
        initial_widgets=initial_widgets,
        pages={"/": "index.html", "/catalog": "index.html"},
        health_payload={"status": "ok", "example": "10_widgets_catalog"},
    )
    return application


app = create_app(include_status_widget=os.getenv("PYWASM_INCLUDE_STATUS_WIDGET") == "0")
