from __future__ import annotations

from pywasm_ui import (
    SliderWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        SliderWidget(id="slider_demo", parent="root", value=35, min_value=0, max_value=100, step=5),
    ]


def create_app():
    return create_widget_example_app(
        title="SliderWidget",
        description="Range slider input.",
        widgets=_build_widgets(),
    )


app = create_app()
