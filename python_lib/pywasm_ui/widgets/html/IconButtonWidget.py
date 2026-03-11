from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget
from ._common import bind_optional_handler, html_widget_kind, init_standard_widget

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


class IconButtonWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        icon: str = "*",
        text: str = "",
        enabled: bool = True,
        classes: list[str] | None = None,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
        on_click: "CompatibleEventHandler | None" = None,
    ) -> None:
        label = f"{icon} {text}".strip()
        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="button",
            text_prop="text",
            event="click",
            defaults={
                "text": label,
                "enabled": enabled,
                "classes": classes or ["icon-button"],
            },
            props=props,
            style=style,
        )
        bind_optional_handler(self, "click", on_click)
