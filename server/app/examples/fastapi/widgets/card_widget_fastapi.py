from __future__ import annotations

from pywasm_ui import (
    CardWidget,
    LabelWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        CardWidget(id="card_demo", parent="root"),
        LabelWidget(id="card_label", parent="card_demo", text="Contenu de la card"),
    ]


def create_app():
    return create_widget_example_app(
        title="CardWidget",
        description="Card container with a label inside.",
        widgets=_build_widgets(),
    )


app = create_app()
