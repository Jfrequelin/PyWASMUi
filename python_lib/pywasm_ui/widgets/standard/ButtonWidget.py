from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget, merge_style_props

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


class ButtonWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "Button",
        enabled: bool = True,
        classes: list[str] | None = None,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
        on_click: "CompatibleEventHandler | None" = None,
    ) -> None:
        merged_props = {
            "__tag": "button",
            "__text_prop": "text",
            "__event": "click",
            "text": text,
            "enabled": enabled,
            "classes": classes or [],
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Button",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
        if on_click is not None:
            self.on("click", on_click)
