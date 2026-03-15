from __future__ import annotations

from pywasm_ui import (
    SpinnerWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        SpinnerWidget(id="spinner_demo", parent="root", label="Chargement"),
    ]


def create_app():
    return create_widget_example_app(
        title="SpinnerWidget",
        description="Loading spinner widget.",
        widgets=_build_widgets(),
    )


app = create_app()
