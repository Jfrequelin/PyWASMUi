from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import init_standard_widget


class TextInputWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        value: str = "",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag="input",
            event="change",
            defaults={
                "input_type": "text",
                "value": value,
            },
            props=props,
            style=style,
        )
