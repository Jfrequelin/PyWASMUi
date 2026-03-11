from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class StackWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        gap: str = "8px",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="div",
            defaults={"classes": ["stack"]},
            props=props,
            style=style,
            default_style={
                "display": "flex",
                "flex-direction": "column",
                "gap": gap,
            },
        )
