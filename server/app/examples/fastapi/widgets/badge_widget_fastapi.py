from __future__ import annotations

from pywasm_ui import (
    BadgeWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        BadgeWidget(id="badge_demo", parent="root", text="Nouveau", variant="success"),
    ]


def create_app():
    return create_widget_example_app(
        title="BadgeWidget",
        description="Simple status badge.",
        widgets=_build_widgets(),
    )


app = create_app()
