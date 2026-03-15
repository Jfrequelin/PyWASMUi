from __future__ import annotations

from pywasm_ui import (
    ConnectionStatusWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ConnectionStatusWidget(id="connection_status_demo", parent="root", state="connected"),
    ]


def create_app():
    return create_widget_example_app(
        title="ConnectionStatusWidget",
        description="Connection status indicator widget.",
        widgets=_build_widgets(),
    )


app = create_app()
