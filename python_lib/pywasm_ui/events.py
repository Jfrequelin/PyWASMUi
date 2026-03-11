from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pywasm_ui.protocol import EventPayload


@dataclass(frozen=True)
class UiEvent:
    kind: str
    widget_id: str
    value: Any
    nonce: int | None
    raw: EventPayload


@dataclass(frozen=True)
class ClickEvent(UiEvent):
    pass


@dataclass(frozen=True)
class ChangeEvent(UiEvent):
    pass


@dataclass(frozen=True)
class TextInputChangeEvent(ChangeEvent):
    @property
    def text(self) -> str:
        return "" if self.value is None else str(self.value)


@dataclass(frozen=True)
class SliderChangeEvent(ChangeEvent):
    @property
    def number(self) -> float | None:
        if isinstance(self.value, bool):
            return None
        if isinstance(self.value, (int, float)):
            return float(self.value)
        if isinstance(self.value, str):
            try:
                return float(self.value)
            except ValueError:
                return None
        return None


def to_typed_event(event: EventPayload) -> UiEvent:
    base_kwargs = {
        "kind": event.kind,
        "widget_id": event.id,
        "value": event.value,
        "nonce": event.nonce,
        "raw": event,
    }

    if event.kind == "click":
        return ClickEvent(**base_kwargs)

    if event.kind == "change":
        if isinstance(event.value, str):
            return TextInputChangeEvent(**base_kwargs)
        return SliderChangeEvent(**base_kwargs)

    return UiEvent(**base_kwargs)
