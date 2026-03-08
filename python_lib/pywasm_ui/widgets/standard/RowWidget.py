from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


class RowWidget(WasmWidget):
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
            "classes": ["row"],
            **(props or {}),
        }
        props_with_default_style = merge_style_props(
            merged_props,
            {
                "display": "flex",
                "align-items": "center",
                "gap": gap,
            },
        )
        super().__init__(
            id=id,
            kind="Row",
            parent=parent,
            props=merge_style_props(props_with_default_style, style),
            children=[],
        )
