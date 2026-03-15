from __future__ import annotations

from pywasm_ui import (
    StackWidget,
    LabelWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        StackWidget(id="stack_demo", parent="root", gap="6px"),
        LabelWidget(id="stack_label_1", parent="stack_demo", text="Ligne 1"),
        LabelWidget(id="stack_label_2", parent="stack_demo", text="Ligne 2"),
    ]


def create_app():
    return create_widget_example_app(
        title="StackWidget",
        description="Vertical stack layout with labels.",
        widgets=_build_widgets(),
    )


app = create_app()
