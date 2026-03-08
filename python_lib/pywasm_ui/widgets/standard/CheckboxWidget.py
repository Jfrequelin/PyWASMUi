from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget, merge_style_props

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


class CheckboxWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        checked: bool = False,
        value: str = "1",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
        on_change: "CompatibleEventHandler | None" = None,
    ) -> None:
        attrs = {"value": value}
        if checked:
            attrs["checked"] = "true"

        merged_props = {
            "__tag": "input",
            "__event": "change",
            "input_type": "checkbox",
            "value": value,
            "attrs": attrs,
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="Checkbox",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )
        if on_change is not None:
            self.on("change", on_change)
