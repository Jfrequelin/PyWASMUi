from __future__ import annotations

from pywasm_ui import (
    OptionWidget,
    SelectWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        SelectWidget(id="select_demo", parent="root"),
        OptionWidget(id="select_option_1", parent="select_demo", text="Option 1", value="1", selected=True),
        OptionWidget(id="select_option_2", parent="select_demo", text="Option 2", value="2"),
    ]


def create_app():
    return create_widget_example_app(
        title="SelectWidget",
        description="Select input with two options.",
        widgets=_build_widgets(),
    )


app = create_app()
