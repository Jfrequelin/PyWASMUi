from __future__ import annotations

from pywasm_ui import (
    VideoWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        VideoWidget(id="video_demo", parent="root", src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4", muted=True),
    ]


def create_app():
    return create_widget_example_app(
        title="VideoWidget",
        description="Video player widget with controls.",
        widgets=_build_widgets(),
    )


app = create_app()
