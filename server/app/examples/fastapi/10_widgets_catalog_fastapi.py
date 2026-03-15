"""Example 10: full widget catalog showcase, implemented step by step."""

import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from pywasm_ui import (
    AccordionHeaderWidget,
    AccordionItemWidget,
    AccordionWidget,
    AlertWidget,
    AudioWidget,
    BarChartWidget,
    BadgeWidget,
    ButtonWidget,
    CardWidget,
    CheckboxWidget,
    ConnectionStatusWidget,
    ContainerWidget,
    DatePickerWidget,
    DividerWidget,
    HeadingWidget,
    ImageWidget,
    IconButtonWidget,
    LabelWidget,
    LinkWidget,
    ListViewWidget,
    ModalWidget,
    OptionWidget,
    ParagraphWidget,
    CodeBlockWidget,
    ProgressWidget,
    PyWasmSession,
    RowWidget,
    SelectWidget,
    SliderWidget,
    SpinnerWidget,
    StackWidget,
    Style,
    TabItemWidget,
    TabsWidget,
    TextAreaWidget,
    TextInputWidget,
    VideoWidget,
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
    chart_values = [max(8, next_value // 3), max(12, next_value // 2), next_value]
    return [
        session.update("task_progress", attrs={"value": str(next_value), "max": "100"}),
        session.update(
            "chart_feedback",
            attrs={"data-chart-values": json.dumps(chart_values, ensure_ascii=True)},
        ),
        session.update("badge_state", text=f"Progression mise a jour: {next_value}%"),
    ]


def _next_chart_window(session: PyWasmSession) -> tuple[list[int], list[str], int]:
    history = session.data.get("chart_history")
    if not isinstance(history, list):
        history = [24, 42, 72]

    tick = _safe_int(session.data.get("chart_tick"), default=len(history)) + 1
    next_value = random.randint(8, 100)

    numeric_history = [
        _safe_int(value, default=0)
        for value in history
    ]
    numeric_history.append(next_value)
    window = numeric_history[-12:]

    labels = [f"t{index}" for index in range(tick - len(window) + 1, tick + 1)]

    session.data["chart_history"] = window
    session.data["chart_tick"] = tick

    return window, labels, next_value


def on_chart_stream_tick(session: PyWasmSession) -> list[CallbackResponse]:
    values, labels, latest = _next_chart_window(session)
    return [
        session.update(
            "chart_feedback",
            attrs={
                "data-chart-values": json.dumps(values, ensure_ascii=True),
                "data-chart-labels": json.dumps(labels, ensure_ascii=True),
                "data-chart-max": "100",
            },
        ),
        session.update("label_chart_latest", text=f"Derniere valeur serveur: {latest}"),
        session.update("badge_state", text=f"Flux chart: nouveau point {latest}"),
    ]


def on_chart_stream_burst(session: PyWasmSession) -> list[CallbackResponse]:
    values: list[int] = []
    labels: list[str] = []
    latest = 0
    for _ in range(5):
        values, labels, latest = _next_chart_window(session)

    return [
        session.update(
            "chart_feedback",
            attrs={
                "data-chart-values": json.dumps(values, ensure_ascii=True),
                "data-chart-labels": json.dumps(labels, ensure_ascii=True),
                "data-chart-max": "100",
            },
        ),
        session.update("label_chart_latest", text=f"Derniere valeur serveur: {latest}"),
        session.update("badge_state", text="Flux chart: defilement accelere (5 points)"),
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


def _activate_demo_tab(session: PyWasmSession, active_tab: str) -> list[CallbackResponse]:
    tabs = [
        ("overview", "tab_demo_overview", "tab_panel_overview"),
        ("metrics", "tab_demo_metrics", "tab_panel_metrics"),
        ("settings", "tab_demo_settings", "tab_panel_settings"),
    ]
    responses: list[CallbackResponse] = [
        session.update("tab_active_value", text=f"Onglet actif: {active_tab.title()}"),
        session.update("badge_state", text=f"Navigation onglets: {active_tab}"),
    ]
    for value, tab_id, panel_id in tabs:
        is_active = value == active_tab
        responses.append(
            session.update(
                tab_id,
                attrs={"aria-selected": "true" if is_active else "false"},
                style={
                    "border-bottom": "2px solid #0f766e" if is_active else "2px solid transparent",
                    "font-weight": "700" if is_active else "500",
                    "opacity": "1" if is_active else "0.7",
                },
            )
        )
        responses.append(
            session.update(
                panel_id,
                style={
                    "display": "block" if is_active else "none",
                },
            )
        )
    return responses


def on_tab_overview_click(session: PyWasmSession) -> list[CallbackResponse]:
    return _activate_demo_tab(session, "overview")


def on_tab_metrics_click(session: PyWasmSession) -> list[CallbackResponse]:
    return _activate_demo_tab(session, "metrics")


def on_tab_settings_click(session: PyWasmSession) -> list[CallbackResponse]:
    return _activate_demo_tab(session, "settings")


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
        HeadingWidget(id="heading_features_themes", parent="stack_features", text="Widgets organises par theme", level=3),
        ParagraphWidget(
            id="paragraph_features_themes",
            parent="stack_features",
            text="Cette section regroupe les widgets par usage: organisation, media et data/feedback.",
        ),
        DividerWidget(id="divider_theme_organisation", parent="stack_features"),
        HeadingWidget(id="heading_theme_organisation", parent="stack_features", text="Theme: Organisation", level=4),
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
        HeadingWidget(id="heading_tabs_accordion", parent="stack_features", text="Sous-theme: Navigation (Tabs + Accordion)", level=4),
        ParagraphWidget(
            id="paragraph_tabs_accordion_intro",
            parent="stack_features",
            text="Tabs et Accordion permettent de structurer des contenus longs sans surcharger la page.",
        ),
        TabsWidget(id="tabs_demo", parent="stack_features"),
        TabItemWidget(
            id="tab_demo_overview",
            parent="tabs_demo",
            text="Overview",
            value="overview",
            selected=True,
            on_click=on_tab_overview_click,
        ),
        TabItemWidget(
            id="tab_demo_metrics",
            parent="tabs_demo",
            text="Metrics",
            value="metrics",
            on_click=on_tab_metrics_click,
        ),
        TabItemWidget(
            id="tab_demo_settings",
            parent="tabs_demo",
            text="Settings",
            value="settings",
            on_click=on_tab_settings_click,
        ),
        LabelWidget(id="tab_active_value", parent="stack_features", text="Onglet actif: Overview"),
        ContainerWidget(
            id="tab_panels_demo",
            parent="stack_features",
            style=Style(border="1px solid #e2e8f0", border_radius="8px", padding="10px"),
        ),
        ContainerWidget(id="tab_panel_overview", parent="tab_panels_demo", style=Style(display="block")),
        ParagraphWidget(
            id="tab_panel_overview_text",
            parent="tab_panel_overview",
            text="Overview: utilisez TabsWidget pour separer des contenus sans changer de page.",
        ),
        ContainerWidget(id="tab_panel_metrics", parent="tab_panels_demo", style=Style(display="none")),
        ParagraphWidget(
            id="tab_panel_metrics_text",
            parent="tab_panel_metrics",
            text="Metrics: ce panneau peut presenter des indicateurs, courbes ou etats temps reel.",
        ),
        ContainerWidget(id="tab_panel_settings", parent="tab_panels_demo", style=Style(display="none")),
        ParagraphWidget(
            id="tab_panel_settings_text",
            parent="tab_panel_settings",
            text="Settings: placez ici des formulaires de configuration contextuelle.",
        ),
        AccordionWidget(id="accordion_demo", parent="stack_features"),
        AccordionItemWidget(id="accordion_demo_item_1", parent="accordion_demo", open_by_default=True),
        AccordionHeaderWidget(id="accordion_demo_item_1_header", parent="accordion_demo_item_1", text="Qu'est-ce que TabsWidget ?"),
        ParagraphWidget(
            id="accordion_demo_item_1_content",
            parent="accordion_demo_item_1",
            text="TabsWidget permet d'organiser des vues en onglets cliquables cote serveur.",
        ),
        AccordionItemWidget(id="accordion_demo_item_2", parent="accordion_demo"),
        AccordionHeaderWidget(id="accordion_demo_item_2_header", parent="accordion_demo_item_2", text="Qu'est-ce que AccordionWidget ?"),
        ParagraphWidget(
            id="accordion_demo_item_2_content",
            parent="accordion_demo_item_2",
            text="AccordionWidget structure des sections repliables composees avec details/summary.",
        ),
        AccordionItemWidget(id="accordion_demo_item_3", parent="accordion_demo"),
        AccordionHeaderWidget(
            id="accordion_demo_item_3_header",
            parent="accordion_demo_item_3",
            text="Quand utiliser Tabs vs Accordion ?",
        ),
        ParagraphWidget(
            id="accordion_demo_item_3_content",
            parent="accordion_demo_item_3",
            text=(
                "Tabs: navigation horizontale entre sections equivalentes. "
                "Accordion: details progressifs sur une liste de sujets."
            ),
        ),
        DividerWidget(id="divider_theme_media", parent="stack_features"),
        HeadingWidget(id="heading_theme_media", parent="stack_features", text="Theme: Media et ressources", level=4),
        ParagraphWidget(
            id="paragraph_rich_content_intro",
            parent="stack_features",
            text="Ce bloc montre des contenus riches (lien, image, extrait de code) composes cote serveur.",
        ),
        LinkWidget(
            id="link_demo_docs",
            parent="stack_features",
            text="Ouvrir la documentation PyWASMui",
            href="https://github.com/Jfrequelin/PyWASMUi",
            target="_blank",
            rel="noopener noreferrer",
        ),
        ImageWidget(
            id="image_demo_preview",
            parent="stack_features",
            src=(
                "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 420 140'%3E"
                "%3Crect width='420' height='140' fill='%23e2e8f0'/%3E"
                "%3Crect x='10' y='10' width='400' height='120' rx='10' fill='%230f172a'/%3E"
                "%3Ctext x='24' y='72' fill='%23e2e8f0' font-size='20' font-family='monospace'%3E"
                "PyWASMui ImageWidget demo%3C/text%3E%3C/svg%3E"
            ),
            alt="Apercu ImageWidget",
            style=Style(max_width="100%", border="1px solid #e2e8f0", border_radius="6px"),
        ),
        CodeBlockWidget(
            id="code_demo_snippet",
            parent="stack_features",
            language="python",
            text=(
                "from pywasm_ui import pywasm_ui\n"
                "pywasm_ui.fastapi.bootstrap_app(app, frontend_root)"
            ),
            style=Style(background_color="#0f172a", color="#e2e8f0", padding="10px", border_radius="6px"),
        ),
        VideoWidget(
            id="video_demo_preview",
            parent="stack_features",
            src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
            muted=True,
            style=Style(max_width="100%", border_radius="8px", border="1px solid #e2e8f0"),
        ),
        AudioWidget(
            id="audio_demo_preview",
            parent="stack_features",
            src="https://interactive-examples.mdn.mozilla.net/media/examples/t-rex-roar.mp3",
            style=Style(width="100%"),
        ),
        DividerWidget(id="divider_theme_feedback", parent="stack_features"),
        HeadingWidget(id="heading_theme_feedback", parent="stack_features", text="Theme: Data et feedback", level=4),
        RowWidget(id="row_theme_feedback", parent="stack_features", gap="10px"),
        BadgeWidget(id="badge_state", parent="row_theme_feedback", text="Derniere action: pret", variant="info"),
        BadgeWidget(id="badge_feedback_info", parent="row_theme_feedback", text="Info", variant="info"),
        BadgeWidget(id="badge_feedback_success", parent="row_theme_feedback", text="Success", variant="success"),
        ProgressWidget(id="progress_theme_feedback", parent="stack_features", value=72, max_value=100),
        BarChartWidget(
            id="chart_feedback",
            parent="stack_features",
            labels=["t1", "t2", "t3"],
            values=[24, 42, 72],
            max_value=100,
            title="Progression feedback",
            style=Style(width="100%", margin_top="8px"),
        ),
        RowWidget(id="row_chart_controls", parent="stack_features", gap="8px"),
        ButtonWidget(id="btn_chart_tick", parent="row_chart_controls", text="+1 point serveur", on_click=on_chart_stream_tick),
        ButtonWidget(id="btn_chart_burst", parent="row_chart_controls", text="Defilement x5", on_click=on_chart_stream_burst),
        LabelWidget(id="label_chart_latest", parent="stack_features", text="Derniere valeur serveur: 72"),
        RowWidget(id="row_feedback_loading", parent="stack_features", gap="8px"),
        SpinnerWidget(id="spinner_feedback", parent="row_feedback_loading", label="Chargement des donnees"),
        LabelWidget(id="spinner_feedback_label", parent="row_feedback_loading", text="Traitement en cours..."),
        AlertWidget(
            id="alert_theme_feedback",
            parent="stack_features",
            text="Les widgets de feedback visualisent l'etat des actions et des traitements.",
            level="info",
        ),
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
                z_index="12000",
            ),
        ),
        StackWidget(
            id="stack_interactions",
            parent="card_interactions",
            gap="10px",
            style=Style(position="relative", overflow="visible", z_index="12001"),
        ),
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
