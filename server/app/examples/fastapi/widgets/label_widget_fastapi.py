from __future__ import annotations

from pywasm_ui import (
    LabelWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        LabelWidget(id="label_demo", parent="root", text="Texte label"),
    ]


def create_app():
    return create_widget_example_app(
        title="LabelWidget",
        description="Simple text label.",
        widgets=_build_widgets(),
    )


app = create_app()
