from __future__ import annotations

from pywasm_ui import (
    LinkWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        LinkWidget(id="link_demo", parent="root", text="PyWASM", href="https://example.com", target="_blank"),
    ]


def create_app():
    return create_widget_example_app(
        title="LinkWidget",
        description="Hyperlink widget.",
        widgets=_build_widgets(),
    )


app = create_app()
