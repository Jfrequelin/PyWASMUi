from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


class ListViewWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        merged_props = {"__tag": "div", **(props or {})}
        super().__init__(
            id=id,
            kind="ListView",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
