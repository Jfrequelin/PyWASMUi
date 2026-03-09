from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import init_standard_widget


class AlertWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "Alert",
        level: str = "info",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag="div",
            text_prop="text",
            defaults={
                "text": text,
                "classes": ["alert", f"alert-{level}"],
            },
            props=props,
            style=style,
        )
