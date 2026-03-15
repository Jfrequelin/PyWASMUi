from __future__ import annotations

from pywasm_ui import (
    RowWidget,
    LabelWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        RowWidget(id="row_demo", parent="root", gap="12px"),
        LabelWidget(id="row_label_1", parent="row_demo", text="Colonne A"),
        LabelWidget(id="row_label_2", parent="row_demo", text="Colonne B"),
    ]


def create_app():
    return create_widget_example_app(
        title="RowWidget",
        description="Horizontal row layout with labels.",
        widgets=_build_widgets(),
    )


app = create_app()
