from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


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
        merged_props = {
            "__tag": "progress",
            "attrs": {
                "value": str(value),
                "max": str(max_value),
            },
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Progress",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
