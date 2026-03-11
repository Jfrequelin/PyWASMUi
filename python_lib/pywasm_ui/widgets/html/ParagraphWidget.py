from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class ParagraphWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="p",
            text_prop="text",
            defaults={"text": text},
            props=props,
            style=style,
        )
