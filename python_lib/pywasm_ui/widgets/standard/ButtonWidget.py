from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget
from ._common import bind_optional_handler, init_standard_widget

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
        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag="button",
            text_prop="text",
            event="click",
            defaults={
                "text": text,
                "enabled": enabled,
                "classes": classes or [],
            },
            props=props,
            style=style,
        )
        bind_optional_handler(self, "click", on_click)
