from __future__ import annotations

from pywasm_ui import (
    OptionWidget,
    SelectWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        SelectWidget(id="select_for_option", parent="root"),
        OptionWidget(id="option_demo", parent="select_for_option", text="Choix A", value="a", selected=True),
    ]


def create_app():
    return create_widget_example_app(
        title="OptionWidget",
        description="Select option rendered under a SelectWidget.",
        widgets=_build_widgets(),
    )


app = create_app()
