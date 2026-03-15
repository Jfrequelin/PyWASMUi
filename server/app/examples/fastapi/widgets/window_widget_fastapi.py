from __future__ import annotations

from pywasm_ui import (
    WindowWidget,
    LabelWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        WindowWidget(id="window_demo", parent="root"),
        LabelWidget(id="window_label", parent="window_demo", text="Contenu de fenetre"),
    ]


def create_app():
    return create_widget_example_app(
        title="WindowWidget",
        description="Window-like container with child label.",
        widgets=_build_widgets(),
    )


app = create_app()
