from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import init_standard_widget


class OptionWidget(WasmWidget):  # pylint: disable=super-init-not-called
    def __init__(  # pylint: disable=super-init-not-called
        self,
        id: str,
        parent: str,
        text: str,
        value: str,
        selected: bool = False,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        attrs = {"value": value}
        if selected:
            attrs["selected"] = "true"

        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag="option",
            text_prop="text",
            defaults={
                "text": text,
                "attrs": attrs,
            },
            props=props,
            style=style,
        )
