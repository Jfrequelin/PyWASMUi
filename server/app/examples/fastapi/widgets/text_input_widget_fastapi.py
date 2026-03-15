from __future__ import annotations

from pywasm_ui import (
    TextInputWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        TextInputWidget(id="text_input_demo", parent="root", value="Hello"),
    ]


def create_app():
    return create_widget_example_app(
        title="TextInputWidget",
        description="Single-line text input widget.",
        widgets=_build_widgets(),
    )


app = create_app()
