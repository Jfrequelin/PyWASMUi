from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import init_standard_widget


class HeadingWidget(WasmWidget):  # pylint: disable=super-init-not-called
    def __init__(  # pylint: disable=super-init-not-called
        self,
        id: str,
        parent: str = "root",
        text: str = "Heading",
        level: int = 2,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        bounded_level = max(1, min(6, level))
        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag=f"h{bounded_level}",
            text_prop="text",
            defaults={"text": text},
            props=props,
            style=style,
        )
