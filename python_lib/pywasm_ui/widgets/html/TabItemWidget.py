from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget
from ._common import bind_optional_handler, html_widget_kind, init_standard_widget

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


class TabItemWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str,
        text: str,
        value: str | None = None,
        selected: bool = False,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
        on_click: "CompatibleEventHandler | None" = None,
    ) -> None:
        attrs: dict[str, str] = {
            "type": "button",
            "role": "tab",
            "aria-selected": "true" if selected else "false",
        }
        if value is not None and value.strip():
            attrs["data-tab-value"] = value.strip()

        classes = ["tab-item"]
        if selected:
            classes.append("tab-item-active")

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="button",
            text_prop="text",
            event="click",
            defaults={
                "text": text,
                "attrs": attrs,
                "classes": classes,
            },
            props=props,
            style=style,
        )
        bind_optional_handler(self, "click", on_click)
