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
        marker_attrs = {
            "data-connection-status": "true",
            "data-connection-state": state,
        }
        default_style = {
            "display": "inline-block",
            "padding": "6px 10px",
            "border-radius": "999px",
            "font-size": "12px",
            "font-weight": "700",
            "line-height": "1",
            "border": "1px solid #cbd5e1",
            "background-color": "#f8fafc",
            "color": "#334155",
        }
        merged_props = {
            "__tag": "p",
            "__text_prop": "text",
            "text": _STATUS_TEXT.get(state, "Server: unknown"),
            "attrs": marker_attrs,
            "style": default_style,
        }
        if props:
            merged_props.update(props)
            provided_attrs = props.get("attrs")
            if isinstance(provided_attrs, dict):
                merged_props["attrs"] = {
                    **marker_attrs,
                    **provided_attrs,
                }
        super().__init__(
            id=id,
            kind="Label",
            parent=parent,
            props=merge_style_props(merged_props, style),
            children=[],
        )

    def update_state_patch(self, state: str) -> dict[str, Any]:
        self.props["text"] = _STATUS_TEXT.get(state, "Server: unknown")
        attrs = self.props.setdefault("attrs", {})
        if isinstance(attrs, dict):
            attrs["data-connection-state"] = state
        return {
            "id": self.id,
            "state": state,
            "text": self.props["text"],
            "attrs": {"data-connection-state": state},
        }
