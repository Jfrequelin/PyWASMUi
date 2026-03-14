from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class AccordionItemWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str,
        open_by_default: bool = False,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        attrs = {"open": "true"} if open_by_default else {}

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="details",
            defaults={
                "attrs": attrs,
                "classes": ["accordion-item"],
            },
            props=props,
            style=style,
        )
