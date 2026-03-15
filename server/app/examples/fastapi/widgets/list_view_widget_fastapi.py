from __future__ import annotations

from pywasm_ui import (
    ListViewWidget,
    LabelWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ListViewWidget(id="list_view_demo", parent="root"),
        LabelWidget(id="list_item_1", parent="list_view_demo", text="Element 1"),
        LabelWidget(id="list_item_2", parent="list_view_demo", text="Element 2"),
    ]


def create_app():
    return create_widget_example_app(
        title="ListViewWidget",
        description="List container with labels as rows.",
        widgets=_build_widgets(),
    )


app = create_app()
