from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


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

        merged_props = {
            "__tag": "option",
            "__text_prop": "text",
            "text": text,
            "attrs": attrs,
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Option",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
