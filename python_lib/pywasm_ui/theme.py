from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywasm_ui.session import PyWasmSession


@dataclass(frozen=True)
class ThemeTokens:
    """Simple theme token set for HTML widgets."""

    primary_color: str = "#0ea5e9"
    primary_contrast_color: str = "#ffffff"
    text_color: str = "#111827"
    muted_text_color: str = "#6b7280"
    surface_color: str = "#ffffff"
    border_color: str = "#e5e7eb"
    border_radius: str = "8px"
    spacing: str = "8px"
    font_family: str = "ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"


def apply_theme(session: "PyWasmSession", theme: ThemeTokens | None = None) -> ThemeTokens:
    """Apply theme defaults to a session using existing style-default hooks."""

    resolved = theme or ThemeTokens()
    session.clear_default_styles()

    session.set_default_style_for_kind(
        "Window",
        background_color=resolved.surface_color,
        color=resolved.text_color,
        font_family=resolved.font_family,
    )
    session.set_default_style_for_kind(
        "Card",
        background_color=resolved.surface_color,
        border=f"1px solid {resolved.border_color}",
        border_radius=resolved.border_radius,
        padding=resolved.spacing,
    )
    session.set_default_style_for_kind(
        "Label",
        color=resolved.text_color,
        font_family=resolved.font_family,
    )
    session.set_default_style_for_kind(
        "Paragraph",
        color=resolved.muted_text_color,
        font_family=resolved.font_family,
    )
    session.set_default_style_for_kind(
        "Heading",
        color=resolved.text_color,
        font_family=resolved.font_family,
    )
    session.set_default_style_for_kind(
        "Button",
        border_radius=resolved.border_radius,
        padding=f"calc({resolved.spacing} * 0.75) {resolved.spacing}",
        border="none",
        background_color=resolved.primary_color,
        color=resolved.primary_contrast_color,
    )
    session.set_default_style_for_kind(
        "TextInput",
        border=f"1px solid {resolved.border_color}",
        border_radius=resolved.border_radius,
        padding=f"calc({resolved.spacing} * 0.5)",
        color=resolved.text_color,
        font_family=resolved.font_family,
    )
    session.set_default_style_for_kind(
        "TextArea",
        border=f"1px solid {resolved.border_color}",
        border_radius=resolved.border_radius,
        padding=f"calc({resolved.spacing} * 0.5)",
        color=resolved.text_color,
        font_family=resolved.font_family,
    )
    session.set_default_style_for_kind(
        "Select",
        border=f"1px solid {resolved.border_color}",
        border_radius=resolved.border_radius,
        padding=f"calc({resolved.spacing} * 0.5)",
        color=resolved.text_color,
        font_family=resolved.font_family,
    )

    session.set_default_style_for_class(
        "primary",
        background_color=resolved.primary_color,
        color=resolved.primary_contrast_color,
    )

    return resolved
