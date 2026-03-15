from __future__ import annotations

from pywasm_ui import (
    TextAreaWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        TextAreaWidget(id="text_area_demo", parent="root", value="Ligne 1\nLigne 2"),
    ]


def create_app():
    return create_widget_example_app(
        title="TextAreaWidget",
        description="Multiline text input area.",
        widgets=_build_widgets(),
    )


app = create_app()
