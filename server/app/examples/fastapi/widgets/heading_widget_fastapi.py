from __future__ import annotations

from pywasm_ui import (
    HeadingWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        HeadingWidget(id="heading_demo", parent="root", text="Titre de demonstration", level=3),
    ]


def create_app():
    return create_widget_example_app(
        title="HeadingWidget",
        description="Heading text element.",
        widgets=_build_widgets(),
    )


app = create_app()
