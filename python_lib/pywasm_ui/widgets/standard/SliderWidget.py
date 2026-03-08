from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget, merge_style_props

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


class SliderWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        step: int = 1,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
        on_change: "CompatibleEventHandler | None" = None,
    ) -> None:
        merged_props = {
            "__tag": "input",
            "__event": "change",
            "input_type": "range",
            "value": str(value),
            "attrs": {
                "min": str(min_value),
                "max": str(max_value),
                "step": str(step),
            },
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Slider",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
        if on_change is not None:
            self.on("change", on_change)
