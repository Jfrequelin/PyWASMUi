from __future__ import annotations

from pywasm_ui import (
    IconButtonWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        IconButtonWidget(id="icon_button_demo", parent="root", icon="*", text="Action"),
    ]


def create_app():
    return create_widget_example_app(
        title="IconButtonWidget",
        description="Button with icon and label.",
        widgets=_build_widgets(),
    )


app = create_app()
