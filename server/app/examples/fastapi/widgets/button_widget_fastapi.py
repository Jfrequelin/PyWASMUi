from __future__ import annotations

from pywasm_ui import (
    ButtonWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ButtonWidget(id="button_demo", parent="root", text="Cliquer"),
    ]


def create_app():
    return create_widget_example_app(
        title="ButtonWidget",
        description="Standard clickable button.",
        widgets=_build_widgets(),
    )


app = create_app()
