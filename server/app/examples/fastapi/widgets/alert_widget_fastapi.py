from __future__ import annotations

from pywasm_ui import (
    AlertWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        AlertWidget(id="alert_demo", parent="root", text="Operation reussie", level="success"),
    ]


def create_app():
    return create_widget_example_app(
        title="AlertWidget",
        description="Basic alert with success level.",
        widgets=_build_widgets(),
    )


app = create_app()
