from __future__ import annotations

from pywasm_ui import (
    CheckboxWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        CheckboxWidget(id="checkbox_demo", parent="root", checked=True),
    ]


def create_app():
    return create_widget_example_app(
        title="CheckboxWidget",
        description="Boolean input checkbox.",
        widgets=_build_widgets(),
    )


app = create_app()
