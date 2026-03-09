from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import init_standard_widget


class RowWidget(WasmWidget):  # pylint: disable=super-init-not-called
    def __init__(  # pylint: disable=super-init-not-called
        self,
        id: str,
        parent: str = "root",
        gap: str = "8px",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag="div",
            defaults={"classes": ["row"]},
            props=props,
            style=style,
            default_style={
                "display": "flex",
                "align-items": "center",
                "gap": gap,
            },
        )
