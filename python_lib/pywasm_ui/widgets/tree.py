from __future__ import annotations

from typing import Any

from .base import WasmWidget


class WidgetTree:
    def __init__(self) -> None:
        self.widgets: dict[str, WasmWidget] = {}

    def upsert(self, widget: WasmWidget) -> None:
        self.widgets[widget.id] = widget

    def get(self, widget_id: str) -> WasmWidget | None:
        return self.widgets.get(widget_id)

    def as_payload(self, widget_id: str) -> dict[str, Any] | None:
        widget = self.get(widget_id)
        if widget is None:
            return None
        return widget.to_payload()
