from __future__ import annotations

from pywasm_ui import (
    ContainerWidget,
    LabelWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ContainerWidget(id="container_demo", parent="root"),
        LabelWidget(id="container_label", parent="container_demo", text="Contenu"),
    ]


def create_app():
    return create_widget_example_app(
        title="ContainerWidget",
        description="Generic container with a child label.",
        widgets=_build_widgets(),
    )


app = create_app()
