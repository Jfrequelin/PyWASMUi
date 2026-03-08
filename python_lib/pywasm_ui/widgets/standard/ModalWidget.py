from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


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

        merged_props = {
            "__tag": "dialog",
            "__text_prop": "text",
            "text": text,
            "attrs": attrs,
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Modal",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
