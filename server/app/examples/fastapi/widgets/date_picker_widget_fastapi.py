from __future__ import annotations

from pywasm_ui import (
    DatePickerWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        DatePickerWidget(id="date_picker_demo", parent="root", value="2026-03-14"),
    ]


def create_app():
    return create_widget_example_app(
        title="DatePickerWidget",
        description="Date picker input field.",
        widgets=_build_widgets(),
    )


app = create_app()
