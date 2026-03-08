from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


class StackWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        gap: str = "8px",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        merged_props = {
            "__tag": "div",
            "classes": ["stack"],
            **(props or {}),
        }
        props_with_default_style = merge_style_props(
            merged_props,
            {
                "display": "flex",
                "flex-direction": "column",
                "gap": gap,
            },
        )
        super().__init__(
            id=id,
            kind="Stack",
            parent=parent,
            props=merge_style_props(props_with_default_style, style),
            children=[],
        )
