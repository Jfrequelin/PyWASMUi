from __future__ import annotations

from typing import Any

from .base import Style, WasmWidget, merge_style_props

_STATUS_TEXT = {
    "connecting": "Server: connecting...",
    "connected": "Server: connected",
    "error": "Server: connection error",
    "closed": "Server: disconnected",
}


class ConnectionStatusWidget(WasmWidget):
    def __init__(
        self,
        id: str = "connection_status",
        parent: str = "root",
        state: str = "connecting",
        props: dict[str, Any] | None = None,
        style: Style | dict[str, Any] | None = None,
    ) -> None:
        merged_props = {
            "__tag": "p",
            "__text_prop": "text",
            "state": state,
            "text": _STATUS_TEXT.get(state, "Server: unknown"),
            **(props or {}),
        }
        super().__init__(
            id=id,
            kind="ConnectionStatus",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )

    def update_state_patch(self, state: str) -> dict[str, str]:
        self.props["state"] = state
        self.props["text"] = _STATUS_TEXT.get(state, "Server: unknown")
        return {"id": self.id, "state": state, "text": self.props["text"]}
