from __future__ import annotations

from pywasm_ui import (
    TabItemWidget,
    TabsWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        TabsWidget(id="tabs_demo", parent="root"),
        TabItemWidget(id="tabs_demo_item_1", parent="tabs_demo", text="General", selected=True),
        TabItemWidget(id="tabs_demo_item_2", parent="tabs_demo", text="Details"),
    ]


def create_app():
    return create_widget_example_app(
        title="TabsWidget",
        description="Tabs container with two tab items.",
        widgets=_build_widgets(),
    )


app = create_app()
