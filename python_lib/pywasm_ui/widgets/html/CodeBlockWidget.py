from __future__ import annotations

from typing import Any

from ..base import Style, WasmWidget
from ._common import html_widget_kind, init_standard_widget


class CodeBlockWidget(WasmWidget):
    def __init__(
        self,
        id: str,
        parent: str = "root",
        text: str = "",
        language: str | None = None,
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        classes = ["code-block"]
        if language is not None and language.strip():
            classes.append(f"language-{language.strip().lower()}")

        super().__init__(id=id, kind=html_widget_kind(self), parent=parent, props={}, children=[])
        init_standard_widget(
            self,
            id=id,
            parent=parent,
            tag="pre",
            text_prop="text",
            defaults={
                "text": text,
                "classes": classes,
            },
            props=props,
            style=style,
        )
