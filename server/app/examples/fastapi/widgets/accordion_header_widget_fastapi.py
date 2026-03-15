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
        AccordionWidget(id="accordion_root", parent="root"),
        AccordionItemWidget(id="accordion_item", parent="accordion_root", open_by_default=True),
        AccordionHeaderWidget(id="accordion_header_demo", parent="accordion_item", text="Header demo"),
    ]


def create_app():
    return create_widget_example_app(
        title="AccordionHeaderWidget",
        description="Accordion header inside an item and accordion.",
        widgets=_build_widgets(),
    )


app = create_app()
