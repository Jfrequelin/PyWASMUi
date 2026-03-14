from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget
from ._common import bind_optional_handler, html_widget_kind, init_standard_widget

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


class LinkWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "Link",
        href: str = "#",
        target: str | None = None,
        rel: str | None = None,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
        on_click: "CompatibleEventHandler | None" = None,
    ) -> None:
        attrs: dict[str, str] = {"href": href}
        if target is not None and target.strip():
            attrs["target"] = target.strip()
        if rel is not None and rel.strip():
            attrs["rel"] = rel.strip()

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="a",
            text_prop="text",
            event="click",
            defaults={
                "text": text,
                "attrs": attrs,
                "classes": ["link-widget"],
            },
            props=props,
            style=style,
        )
        bind_optional_handler(self, "click", on_click)
