from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import init_standard_widget


class ModalWidget(WasmWidget):  # pylint: disable=super-init-not-called
    def __init__(  # pylint: disable=super-init-not-called
        self,
        id: str,
        parent: str = "root",
        text: str = "",
        is_open: bool = False,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        attrs = {}
        if is_open:
            attrs["open"] = "true"

        init_standard_widget(
            self,
            id=id,
            kind=self.__class__.__name__.removesuffix("Widget"),
            parent=parent,
            tag="dialog",
            text_prop="text",
            defaults={
                "text": text,
                "attrs": attrs,
            },
            props=props,
            style=style,
        )
