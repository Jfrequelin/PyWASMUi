from __future__ import annotations

from pywasm_ui import (
    BarChartWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        BarChartWidget(id="bar_chart_demo", parent="root", labels=["A", "B", "C"], values=[12, 28, 19], max_value=30, title="Sales"),
    ]


def create_app():
    return create_widget_example_app(
        title="BarChartWidget",
        description="Server-side configured bar chart rendered in WASM.",
        widgets=_build_widgets(),
    )


app = create_app()
