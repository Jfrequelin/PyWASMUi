from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class AudioWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        src: str = "",
        controls: bool = True,
        autoplay: bool = False,
        loop: bool = False,
        muted: bool = False,
        preload: str = "metadata",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        attrs: dict[str, str] = {
            "src": src,
            "preload": preload,
        }
        if controls:
            attrs["controls"] = "true"
        if autoplay:
            attrs["autoplay"] = "true"
        if loop:
            attrs["loop"] = "true"
        if muted:
            attrs["muted"] = "true"

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="audio",
            defaults={
                "attrs": attrs,
                "classes": ["audio-widget"],
            },
            props=props,
            style=style,
        )
