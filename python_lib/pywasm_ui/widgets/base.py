from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Iterator

from pywasm_ui.session.types import adapt_event_handler

if TYPE_CHECKING:
    from pywasm_ui.session.types import CompatibleEventHandler, EventHandler


_MISSING = object()


class Style:
    def __init__(self, initial: dict[str, Any] | None = None, **properties: Any) -> None:
        self._values: dict[str, str] = {}
        self._on_change: Callable[[dict[str, str]], None] | None = None
        if initial:
            self.set(**initial)
        if properties:
            self.set(**properties)

    def bind_to(self, props: dict[str, Any]) -> "Style":
        self._on_change = lambda values: props.__setitem__("style", values)
        props["style"] = self._values
        return self

    def set(self, name: str | None = None, value: Any = None, **properties: Any) -> "Style":
        if name is not None:
            self._set_single(name, value)
        for key, prop_value in properties.items():
            self._set_single(key, prop_value)
        self._emit_change()
        return self

    def apply(self, *styles: "Style | dict[str, Any] | str", **properties: Any) -> "Style":
        """Apply one or many style sources.

        Accepted forms:
        - Style object
        - style dict (snake_case or kebab-case keys)
        - CSS declaration string, e.g. "color: red; margin-top: 8px"
        """

        for style_input in styles:
            if isinstance(style_input, Style):
                self.set(**style_input.to_dict())
                continue
            if isinstance(style_input, str):
                self.set(**self.parse_css(style_input))
                continue
            if isinstance(style_input, dict):
                self.set(**style_input)
        if properties:
            self.set(**properties)
        return self

    def get(self, name: str, default: Any = None) -> str | Any:
        return self._values.get(self._normalize_name(name), default)

    def remove(self, *names: str) -> "Style":
        for name in names:
            self._values.pop(self._normalize_name(name), None)
        self._emit_change()
        return self

    def clear(self) -> "Style":
        self._values.clear()
        self._emit_change()
        return self

    def to_dict(self) -> dict[str, str]:
        return dict(self._values)

    @classmethod
    def from_any(cls, value: Style | dict[str, Any] | None) -> "Style":
        if isinstance(value, Style):
            return cls(initial=value.to_dict())
        if isinstance(value, dict):
            return cls(initial=value)
        return cls()

    @staticmethod
    def parse_css(css: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for chunk in css.split(";"):
            entry = chunk.strip()
            if not entry:
                continue
            if ":" not in entry:
                continue
            name, raw_value = entry.split(":", 1)
            key = Style._normalize_name(name)
            value = raw_value.strip()
            if not key or not value:
                continue
            parsed[key] = value
        return parsed

    def _emit_change(self) -> None:
        if self._on_change is not None:
            self._on_change(self._values)

    def _set_single(self, name: str, value: Any) -> None:
        normalized_name = self._normalize_name(name)
        if value is None:
            self._values.pop(normalized_name, None)
            return
        self._values[normalized_name] = self._normalize_value(value)

    def __getattr__(self, name: str) -> str | None:
        if name.startswith("__"):
            raise AttributeError(name)
        if "_values" not in self.__dict__:
            raise AttributeError(name)
        # Attribute-style access such as style.margin_top or style.margin.
        return self._values.get(self._normalize_name(name))

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        self._set_single(name, value)
        self._emit_change()

    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.strip().replace("_", "-")

    @staticmethod
    def _normalize_value(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)


class WidgetStyle(Style):
    # Backward-compatible alias for previous API name.
    pass


def style_dict(style: Style | dict[str, Any] | str | None) -> dict[str, str] | None:
    if style is None:
        return None
    if isinstance(style, Style):
        return style.to_dict()
    if isinstance(style, str):
        return Style.parse_css(style)

    normalized: dict[str, str] = {}
    for key, value in style.items():
        normalized_key = Style._normalize_name(key)
        if value is None:
            continue
        normalized[normalized_key] = Style._normalize_value(value)
    return normalized


def merge_style_props(
    props: dict[str, Any],
    style: Style | dict[str, Any] | str | None,
) -> dict[str, Any]:
    merged = dict(props)
    explicit_style = style_dict(style)

    prop_style_raw = merged.get("style")
    prop_style = style_dict(prop_style_raw) if isinstance(prop_style_raw, (dict, Style)) else None

    if prop_style and explicit_style:
        merged["style"] = {**prop_style, **explicit_style}
    elif explicit_style:
        merged["style"] = explicit_style
    elif prop_style:
        merged["style"] = prop_style

    return merged


def normalize_widget_props(props: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(props)
    prop_style = normalized.get("style")
    if isinstance(prop_style, (dict, Style, str)):
        normalized["style"] = style_dict(prop_style)
    return normalized


@dataclass
class WasmWidget:
    id: str
    kind: str
    parent: str
    props: dict[str, Any] = field(default_factory=dict)
    children: list[str] = field(default_factory=list)
    _style_proxy: Style = field(init=False, repr=False, compare=False)
    _event_handlers: dict[str, "EventHandler"] = field(
        default_factory=dict,
        repr=False,
        compare=False,
    )

    def __init__(
        self,
        id: str,
        kind: str,
        parent: str,
        props: dict[str, Any] | None = None,
        children: list[str] | None = None,
    ) -> None:
        self.id = id
        self.kind = kind
        self.parent = parent
        self.props = props or {}
        self.children = children or []
        self._event_handlers = {}
        self.__post_init__()

    def __post_init__(self) -> None:
        self.props = normalize_widget_props(self.props)
        # Base behavior: interactive widgets get a standard pending visual feedback class.
        has_single_event = isinstance(self.props.get("__event"), str)
        has_event_list = isinstance(self.props.get("__events"), list) and any(
            isinstance(event_kind, str) and event_kind
            for event_kind in self.props.get("__events", [])
        )
        if has_single_event or has_event_list:
            self.props.setdefault("__pending_class", "widget-pending")
        initial_style = (
            self.props.get("style")
            if isinstance(self.props.get("style"), (dict, Style))
            else None
        )
        self._style_proxy = Style.from_any(initial_style).bind_to(self.props)

    @property
    def style(self) -> Style:
        return self._style_proxy

    def on(self, event_kind: str, handler: "CompatibleEventHandler") -> "WasmWidget":
        self._event_handlers[event_kind] = adapt_event_handler(handler)
        return self

    def on_click(self, handler: "CompatibleEventHandler") -> "WasmWidget":
        return self.on("click", handler)

    def on_change(self, handler: "CompatibleEventHandler") -> "WasmWidget":
        return self.on("change", handler)

    def on_input(self, handler: "CompatibleEventHandler") -> "WasmWidget":
        return self.on("input", handler)

    def on_hover(self, handler: "CompatibleEventHandler") -> "WasmWidget":
        # Hover semantic is mapped to mouseenter for predictable single-fire behavior.
        return self.on("mouseenter", handler)

    def on_focus(self, handler: "CompatibleEventHandler") -> "WasmWidget":
        return self.on("focus", handler)

    def on_blur(self, handler: "CompatibleEventHandler") -> "WasmWidget":
        return self.on("blur", handler)

    def command(self, handler: "CompatibleEventHandler") -> "WasmWidget":
        # Tkinter-like alias for click callbacks.
        return self.on_click(handler)

    def config(self, **props: Any) -> "WasmWidget":
        # Tkinter-like alias for batched property updates.
        for name, value in props.items():
            self.prop(name, value)
        return self

    def cget(self, name: str) -> Any:
        # Tkinter-like property getter.
        return self.prop(name)

    def prop(self, name: str, value: Any = _MISSING) -> Any:
        if value is _MISSING:
            return self.props.get(name)
        self.props[name] = value
        return self

    def text(self, value: Any = _MISSING) -> Any:
        if value is _MISSING:
            return self.props.get("text")
        self.props["text"] = value
        return self

    def value(self, value: Any = _MISSING) -> Any:
        if value is _MISSING:
            return self.props.get("value")
        self.props["value"] = value
        return self

    def enabled(self, value: Any = _MISSING) -> Any:
        if value is _MISSING:
            return self.props.get("enabled")
        self.props["enabled"] = value
        return self

    def classes(self, value: Any = _MISSING) -> Any:
        if value is _MISSING:
            classes = self.props.get("classes")
            return list(classes) if isinstance(classes, list) else classes
        self.props["classes"] = value
        return self

    def css(self, *styles: Style | dict[str, Any] | str, **properties: Any) -> "WasmWidget":
        # Convenience API for inline CSS updates in one call.
        self.style.apply(*styles, **properties)
        return self

    def add_class(self, *class_names: str) -> "WasmWidget":
        classes = self.classes()
        current = list(classes) if isinstance(classes, list) else []
        for class_name in class_names:
            name = class_name.strip()
            if name and name not in current:
                current.append(name)
        self.classes(current)
        return self

    def remove_class(self, *class_names: str) -> "WasmWidget":
        classes = self.classes()
        current = list(classes) if isinstance(classes, list) else []
        to_remove = {name.strip() for name in class_names if name.strip()}
        self.classes([name for name in current if name not in to_remove])
        return self

    def tooltip(
        self,
        text: str | None,
        *,
        delay_ms: int = 2000,
        include_native_title: bool = False,
    ) -> "WasmWidget":
        """Attach a reusable tooltip to any widget.

        Usage:
            widget.tooltip("Helpful details")
        """

        attrs_raw = self.props.get("attrs")
        attrs: dict[str, Any] = dict(attrs_raw) if isinstance(attrs_raw, dict) else {}

        normalized_text = (text or "").strip()
        if not normalized_text:
            attrs.pop("data-tooltip", None)
            attrs.pop("data-tooltip-delay-ms", None)
            attrs.pop("title", None)
            style_raw = self.props.get("style")
            if isinstance(style_raw, dict):
                style_raw.pop("--pywasm-tooltip-delay-ms", None)
            self.remove_class("pywasm-tooltip-host")
            self.props["attrs"] = attrs
            return self

        safe_delay_ms = max(0, int(delay_ms))
        attrs["data-tooltip"] = normalized_text
        attrs["data-tooltip-delay-ms"] = str(safe_delay_ms)
        if include_native_title:
            attrs["title"] = normalized_text
        else:
            attrs.pop("title", None)

        style_raw = self.props.get("style")
        style_map: dict[str, Any] = dict(style_raw) if isinstance(style_raw, dict) else {}
        style_map["--pywasm-tooltip-delay-ms"] = str(safe_delay_ms)

        self.props["attrs"] = attrs
        self.props["style"] = style_map
        self.add_class("pywasm-tooltip-host")
        return self

    def iter_event_handlers(self) -> Iterator[tuple[str, "EventHandler"]]:
        return iter(self._event_handlers.items())

    def clone(self) -> "WasmWidget":
        cloned = copy.copy(self)
        cloned.props = normalize_widget_props(copy.deepcopy(self.props))
        cloned.children = list(self.children)
        initial_style = (
            cloned.props.get("style")
            if isinstance(cloned.props.get("style"), (dict, Style))
            else None
        )
        cloned._style_proxy = Style.from_any(initial_style).bind_to(cloned.props)
        cloned._event_handlers = dict(self._event_handlers)
        return cloned

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "parent": self.parent,
            "props": normalize_widget_props(self.props),
            "children": self.children,
        }


# Backward-compatible alias.
Widget = WasmWidget
