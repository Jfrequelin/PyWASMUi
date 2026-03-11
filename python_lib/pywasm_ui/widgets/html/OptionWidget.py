from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class OptionWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str,
        text: str,
        value: str,
        selected: bool = False,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        attrs = {"value": value}
        if selected:
            attrs["selected"] = "true"

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])

        init_standard_widget(

            self,
            id=id,
            parent=parent,
            tag="option",
            text_prop="text",
            defaults={
                "text": text,
                "attrs": attrs,
            },
            props=props,
            style=style,
        )
