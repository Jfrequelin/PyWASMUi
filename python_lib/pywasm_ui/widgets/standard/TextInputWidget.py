from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


class TextInputWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        value: str = "",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        merged_props = {
            "__tag": "input",
            "__event": "change",
            "input_type": "text",
            "value": value,
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="TextInput",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
