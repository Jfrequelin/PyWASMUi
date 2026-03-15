from __future__ import annotations

from pywasm_ui import (
    ProgressWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ProgressWidget(id="progress_demo", parent="root", value=64, max_value=100),
    ]


def create_app():
    return create_widget_example_app(
        title="ProgressWidget",
        description="Progress bar widget.",
        widgets=_build_widgets(),
    )


app = create_app()
