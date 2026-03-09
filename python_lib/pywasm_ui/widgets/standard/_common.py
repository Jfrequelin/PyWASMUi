from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..base import Style, WasmWidget, merge_style_props

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler


def build_base_props(
    *,
    tag: str,
    defaults: dict[str, Any] | None = None,
    props: dict[str, Any] | None = None,
    text_prop: str | None = None,
    event: str | None = None,
) -> dict[str, Any]:
    base_props: dict[str, Any] = {"__tag": tag}
    if text_prop is not None:
        base_props["__text_prop"] = text_prop
    if event is not None:
        base_props["__event"] = event
    if defaults:
        base_props.update(defaults)
    if props:
        base_props.update(props)
    return base_props


def init_standard_widget(
    widget: WasmWidget,
    *,
    id: str,
    kind: str,
    parent: str,
    tag: str,
    defaults: dict[str, Any] | None = None,
    props: dict[str, Any] | None = None,
    style: Style | dict[str, Any] | None = None,
    text_prop: str | None = None,
    event: str | None = None,
    default_style: Style | dict[str, Any] | None = None,
) -> None:
    merged_props = build_base_props(
        tag=tag,
        defaults=defaults,
        props=props,
        text_prop=text_prop,
        event=event,
    )
    props_with_default_style = (
        merge_style_props(merged_props, default_style)
        if default_style is not None
        else merged_props
    )
    WasmWidget.__init__(
        widget,
        id=id,
        kind=kind,
        parent=parent,
        props=merge_style_props(props_with_default_style, style),
        children=[],
    )


def bind_optional_handler(
    widget: WasmWidget,
    event_kind: str,
    handler: "CompatibleEventHandler | None",
) -> None:
    if handler is not None:
        widget.on(event_kind, handler)
