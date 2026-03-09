from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import init_standard_widget


class ProgressWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        value: int = 0,
        max_value: int = 100,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag="progress",
            defaults={
                "attrs": {
                    "value": str(value),
                    "max": str(max_value),
                }
            },
            props=props,
            style=style,
        )
