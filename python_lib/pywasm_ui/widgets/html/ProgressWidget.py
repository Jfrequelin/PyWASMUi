from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class ProgressWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        value: int = 0,
        max_value: int = 100,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="progress",
            defaults={
                "attrs": {
                    "value": str(value),
                    "max": str(max_value),
                }
            },
            props=props,
            style=style,
        )
