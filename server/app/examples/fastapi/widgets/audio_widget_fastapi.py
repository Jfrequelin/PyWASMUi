from __future__ import annotations

from pywasm_ui import (
    AudioWidget,
    WasmWidget,
)

from ._common import create_widget_example_app


def _build_widgets() -> list[WasmWidget]:
    return [
        AudioWidget(id="audio_demo", parent="root", src="https://interactive-examples.mdn.mozilla.net/media/examples/t-rex-roar.mp3"),
    ]


def create_app():
    return create_widget_example_app(
        title="AudioWidget",
        description="Audio player widget with controls enabled.",
        widgets=_build_widgets(),
    )


app = create_app()
