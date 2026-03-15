from __future__ import annotations

from pywasm_ui import (
    TabItemWidget,
    TabsWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        TabsWidget(id="tabs_for_item", parent="root"),
        TabItemWidget(id="tab_item_demo", parent="tabs_for_item", text="Tab A", selected=True),
    ]


def create_app():
    return create_widget_example_app(
        title="TabItemWidget",
        description="Single tab item under a tabs container.",
        widgets=_build_widgets(),
    )


app = create_app()
