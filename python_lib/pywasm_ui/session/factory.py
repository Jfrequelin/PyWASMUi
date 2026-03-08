from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Callable, Sequence

from pywasm_ui.security import SecurityManager
from pywasm_ui.widgets import WasmWidget

from .core import PyWasmSession

if TYPE_CHECKING:
    from pywasm_ui.style_template import StyleTemplate


def create_session_factory(
    server_secret: str | bytes,
    initial_widgets: Sequence[WasmWidget] | None = None,
    configure_session: Callable[[PyWasmSession], None] | None = None,
    style_template: StyleTemplate | Mapping[str, Any] | None = None,
) -> Callable[[], PyWasmSession]:
    secret = server_secret.encode("utf-8") if isinstance(server_secret, str) else server_secret
    security_manager = SecurityManager(server_secret=secret)

    style_template_payload: Mapping[str, Any] | None
    if style_template is None:
        style_template_payload = None
    elif isinstance(style_template, Mapping):
        style_template_payload = style_template
    else:
        style_template_payload = style_template.to_dict()

    def factory() -> PyWasmSession:
        session = PyWasmSession(security_manager=security_manager, initial_widgets=initial_widgets)
        if isinstance(style_template_payload, Mapping):
            by_kind = style_template_payload.get("by_kind")
            if isinstance(by_kind, Mapping):
                for kind, style in by_kind.items():
                    if isinstance(kind, str):
                        session.set_default_style_for_kind(kind, style)

            by_class = style_template_payload.get("by_class")
            if isinstance(by_class, Mapping):
                for class_name, style in by_class.items():
                    if isinstance(class_name, str):
                        session.set_default_style_for_class(class_name, style)
        if configure_session is not None:
            configure_session(session)
        return session

    return factory
