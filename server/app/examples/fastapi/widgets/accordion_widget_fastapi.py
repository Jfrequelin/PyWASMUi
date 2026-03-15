from __future__ import annotations

from pywasm_ui import (
    AccordionWidget,
    AccordionItemWidget,
    AccordionHeaderWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        AccordionWidget(id="accordion_demo", parent="root"),
        AccordionItemWidget(id="accordion_item_demo", parent="accordion_demo", open_by_default=True),
        AccordionHeaderWidget(id="accordion_header_demo", parent="accordion_item_demo", text="Section A"),
    ]


def create_app():
    return create_widget_example_app(
        title="AccordionWidget",
        description="Simple accordion container with one item and one header.",
        widgets=_build_widgets(),
    )


app = create_app()
