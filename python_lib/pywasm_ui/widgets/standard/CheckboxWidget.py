from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget
from ._common import bind_optional_handler, init_standard_widget

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


class CheckboxWidget(WasmWidget):  # pylint: disable=super-init-not-called
    def __init__(  # pylint: disable=super-init-not-called
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

        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
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
