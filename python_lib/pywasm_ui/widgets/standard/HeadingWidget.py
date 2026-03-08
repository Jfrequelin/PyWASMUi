from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


class HeadingWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "Heading",
        level: int = 2,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        bounded_level = max(1, min(6, level))
        merged_props = {
            "__tag": f"h{bounded_level}",
            "__text_prop": "text",
            "text": text,
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Heading",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
