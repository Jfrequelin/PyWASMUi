from __future__ import annotations

from pywasm_ui import (
    DividerWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        DividerWidget(id="divider_demo", parent="root"),
    ]


def create_app():
    return create_widget_example_app(
        title="DividerWidget",
        description="Horizontal separator line.",
        widgets=_build_widgets(),
    )


app = create_app()
