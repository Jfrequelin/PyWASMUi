from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


class LabelWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        merged_props = {
            "__tag": "p",
            "__text_prop": "text",
            "text": text,
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Label",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
