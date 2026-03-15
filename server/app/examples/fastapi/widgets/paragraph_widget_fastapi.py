from __future__ import annotations

from pywasm_ui import (
    ParagraphWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ParagraphWidget(id="paragraph_demo", parent="root", text="Exemple de paragraphe pour ce widget."),
    ]


def create_app():
    return create_widget_example_app(
        title="ParagraphWidget",
        description="Paragraph text widget.",
        widgets=_build_widgets(),
    )


app = create_app()
