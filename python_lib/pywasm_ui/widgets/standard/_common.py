"""Backward-compatible alias for HTML widget shared helpers."""

from ..html._common import (
	bind_optional_handler,
	build_base_props,
	html_widget_kind,
	init_standard_widget,
)

__all__ = [
	"build_base_props",
	"html_widget_kind",
	"init_standard_widget",
	"bind_optional_handler",
]
