from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable

from pywasm_ui.protocol import EventPayload, OutgoingMessage

if TYPE_CHECKING:
    from .core import PyWasmSession


CallbackResponse = OutgoingMessage | dict[str, Any] | str | None
EventHandler = Callable[["PyWasmSession", EventPayload], list[CallbackResponse] | CallbackResponse]
CompatibleEventHandler = Callable[..., list[CallbackResponse] | CallbackResponse]


def adapt_event_handler(handler: CompatibleEventHandler) -> EventHandler:
    """Normalize callback signatures to (session, event).

    Supported styles:
    - handler(session, event)
    - handler(session)
    - handler()
    """
    try:
        signature = inspect.signature(handler)
    except (TypeError, ValueError):
        return handler  # type: ignore[return-value]

    positional = [
        param
        for param in signature.parameters.values()
        if param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
    ]
    has_varargs = any(
        param.kind == inspect.Parameter.VAR_POSITIONAL
        for param in signature.parameters.values()
    )

    if has_varargs or len(positional) >= 2:
        return handler  # type: ignore[return-value]

    if len(positional) == 1:
        return lambda session, _event: handler(session)

    return lambda _session, _event: handler()
