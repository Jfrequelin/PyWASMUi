from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_transport_value(value: Any) -> Any:
    """Convert values to a JSON-safe transport shape.

    This keeps protocol messages serializable even if callbacks return Python
    values such as tuples, sets, paths, or custom objects.
    """

    normalized: Any = value
    if value is None or isinstance(value, (bool, int, float, str)):
        normalized = value
    elif isinstance(value, dict):
        normalized = {
            str(key): normalize_transport_value(item)
            for key, item in value.items()
        }
    elif isinstance(value, (list, tuple, set)):
        normalized = [normalize_transport_value(item) for item in value]
    elif isinstance(value, BaseModel):
        normalized = normalize_transport_value(value.model_dump(mode="json"))
    elif hasattr(value, "to_dict"):
        try:
            normalized = normalize_transport_value(value.to_dict())
        except (TypeError, ValueError):
            normalized = str(value)
    else:
        normalized = str(value)
    return normalized


class SessionRef(BaseModel):
    token: str


class WidgetPayload(BaseModel):
    id: str
    kind: str
    parent: str
    props: dict[str, Any] = Field(default_factory=dict)
    children: list[str] = Field(default_factory=list)

    @field_validator("props", mode="before")
    @classmethod
    def _normalize_props(cls, value: Any) -> dict[str, Any]:
        normalized = normalize_transport_value(value)
        return normalized if isinstance(normalized, dict) else {}

    @field_validator("children", mode="before")
    @classmethod
    def _normalize_children(cls, value: Any) -> list[str]:
        normalized = normalize_transport_value(value)
        if not isinstance(normalized, list):
            return []
        return [str(item) for item in normalized]


class OutgoingMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    protocol: Literal[1] = 1
    session: SessionRef | None = None
    type: str
    widget: WidgetPayload | None = None
    patch: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
    client_secret: str | None = None

    @field_validator("patch", "meta", mode="before")
    @classmethod
    def _normalize_dict_fields(cls, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        normalized = normalize_transport_value(value)
        return normalized if isinstance(normalized, dict) else {}


class EventPayload(BaseModel):
    kind: str
    id: str
    value: Any = None
    nonce: int | None = None


class EventMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    protocol: Literal[1]
    type: Literal["event"]
    session: SessionRef
    event: EventPayload
    mac: str | None = None


class ReceiptPayload(BaseModel):
    command_id: str
    status: str | None = None


class ReceiptMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    protocol: Literal[1]
    type: Literal["receipt"]
    session: SessionRef
    receipt: ReceiptPayload
