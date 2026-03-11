from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class ModalWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "",
        is_open: bool = False,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        attrs = {}
        if is_open:
            attrs["open"] = "true"

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])

        init_standard_widget(

            self,
            id=id,
            parent=parent,
            tag="dialog",
            text_prop="text",
            defaults={
                "text": text,
                "attrs": attrs,
            },
            props=props,
            style=style,
        )
