from __future__ import annotations

from pywasm_ui import (
    ImageWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        ImageWidget(id="image_demo", parent="root", src="https://picsum.photos/seed/pywasm/420/200", alt="Demo"),
    ]


def create_app():
    return create_widget_example_app(
        title="ImageWidget",
        description="Image widget with remote source.",
        widgets=_build_widgets(),
    )


app = create_app()
