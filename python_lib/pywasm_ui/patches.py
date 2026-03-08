from __future__ import annotations

from typing import Any

from .widgets.base import Style, style_dict


def set_text(widget_id: str, text: str) -> dict[str, Any]:
    return {"id": widget_id, "text": text}


def patch_value(widget_id: str, value: str) -> dict[str, Any]:
    return {"id": widget_id, "value": value}


def patch_enabled(widget_id: str, enabled: bool) -> dict[str, Any]:
    return {"id": widget_id, "enabled": enabled}


def patch_classes(widget_id: str, classes: list[str]) -> dict[str, Any]:
    return {"id": widget_id, "classes": classes}


def patch_attrs(widget_id: str, attrs: dict[str, Any]) -> dict[str, Any]:
    return {"id": widget_id, "attrs": attrs}


def patch_style(
    widget_id: str,
    style: Style | dict[str, Any] | str | None = None,
    **properties: Any,
) -> dict[str, Any]:
    base_style = style_dict(style)
    extra_style = style_dict(properties) if properties else None

    if base_style and extra_style:
        normalized = {**base_style, **extra_style}
    else:
        normalized = base_style or extra_style

    return {"id": widget_id, "style": normalized or {}}


def patch_remove_attrs(widget_id: str, remove_attrs: list[str]) -> dict[str, Any]:
    return {"id": widget_id, "remove_attrs": remove_attrs}


def merge_patches(widget_id: str, *patches: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {"id": widget_id}
    for patch in patches:
        for key, value in patch.items():
            if key == "id":
                continue
            merged[key] = value
    return merged
