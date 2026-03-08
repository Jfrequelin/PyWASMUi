from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget, merge_style_props


class BadgeWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "Badge",
        variant: str = "default",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        merged_props = {
            "__tag": "span",
            "__text_prop": "text",
            "text": text,
            "classes": ["badge", f"badge-{variant}"],
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Badge",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
