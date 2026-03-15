from __future__ import annotations

from pywasm_ui import (
    ModalWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ModalWidget(id="modal_demo", parent="root", text="Contenu modal", is_open=True),
    ]


def create_app():
    return create_widget_example_app(
        title="ModalWidget",
        description="Open modal/dialog widget.",
        widgets=_build_widgets(),
    )


app = create_app()
