from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class SpinnerWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        label: str = "Chargement",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="div",
            defaults={
                "attrs": {
                    "role": "status",
                    "aria-label": label,
                },
                "classes": ["spinner-widget"],
            },
            props=props,
            style=style,
            default_style={
                "width": "24px",
                "height": "24px",
            },
        )
