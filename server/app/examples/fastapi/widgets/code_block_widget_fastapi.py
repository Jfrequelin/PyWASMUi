from __future__ import annotations

from pywasm_ui import (
    CodeBlockWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        CodeBlockWidget(id="code_block_demo", parent="root", text="print(\"hello\")", language="python"),
    ]


def create_app():
    return create_widget_example_app(
        title="CodeBlockWidget",
        description="Formatted code block widget.",
        widgets=_build_widgets(),
    )


app = create_app()
