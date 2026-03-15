from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class VideoWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        src: str = "",
        controls: bool = True,
        autoplay: bool = False,
        loop: bool = False,
        muted: bool = False,
        poster: str | None = None,
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
        if poster is not None and poster.strip():
            attrs["poster"] = poster.strip()

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="video",
            defaults={
                "attrs": attrs,
                "classes": ["video-widget"],
            },
            props=props,
            style=style,
        )
