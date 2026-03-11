from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget
from ._common import bind_optional_handler, html_widget_kind, init_standard_widget

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

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])

        init_standard_widget(

            self,
            id=id,
            parent=parent,
            tag="input",
            event="change",
            defaults={
                "input_type": "checkbox",
                "value": value,
                "attrs": attrs,
            },
            props=props,
            style=style,
        )
        bind_optional_handler(self, "change", on_change)
