from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class ImageWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        src: str = "",
        alt: str = "",
        lazy: bool = True,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        attrs: dict[str, str] = {
            "src": src,
            "alt": alt,
            "loading": "lazy" if lazy else "eager",
        }

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="img",
            defaults={
                "attrs": attrs,
                "classes": ["image-widget"],
            },
            props=props,
            style=style,
        )
