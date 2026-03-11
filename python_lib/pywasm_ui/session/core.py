from __future__ import annotations

import re
import uuid
import json
from typing import Any, Sequence
from pydantic import ValidationError

from pywasm_ui.protocol import (
    EventMessage,
    EventPayload,
    OutgoingMessage,
    ReceiptMessage,
    SessionRef,
    WidgetPayload,
)
from pywasm_ui.security import SecurityManager
from pywasm_ui.components import render_component_widgets
from pywasm_ui.events import to_typed_event
from pywasm_ui.widgets import ButtonWidget, LabelWidget, Style, WasmWidget, WidgetTree
from pywasm_ui.widgets.base import style_dict

from .context import SessionContext
from .errors import ProtocolViolationError
from .types import CallbackResponse, CompatibleEventHandler, EventHandler, adapt_event_handler


class PyWasmSession:
    def __init__(
        self,
        security_manager: SecurityManager,
        initial_widgets: Sequence[WasmWidget] | None = None,
    ) -> None:
        self._security = security_manager
        self._state = SessionContext(security=security_manager.create_session(), tree=WidgetTree())
        self._initial_widgets = (
            list(initial_widgets)
            if initial_widgets is not None
            else self._default_widgets()
        )
        self._event_handlers: dict[tuple[str, str], EventHandler] = {}
        self._default_handler: EventHandler | None = None
        self._bootstrapped = False
        self._replay_commands: list[str] = []
        self._default_style_by_kind: dict[str, dict[str, str]] = {}
        self._default_style_by_class: dict[str, dict[str, str]] = {}
        self._pending_outbound_command_ids: set[str] = set()
        self.data: dict[str, Any] = {}

    @property
    def session_token(self) -> str:
        return self._state.security.session_token

    @property
    def client_secret(self) -> str:
        return self._state.security.client_secret

    def _default_widgets(self) -> list[WasmWidget]:
        return [
            LabelWidget(id="label1", parent="root", text="Pret"),
            ButtonWidget(id="btn1", parent="root", text="OK", enabled=True, classes=["primary"]),
        ]

    def register_event_handler(
        self,
        event_kind: str,
        widget_id: str,
        handler: CompatibleEventHandler,
    ) -> None:
        self._event_handlers[(event_kind, widget_id)] = adapt_event_handler(handler)

    def register_typed_event_handler(
        self,
        event_kind: str,
        widget_id: str,
        handler: CompatibleEventHandler,
    ) -> None:
        def _wrapped(session: "PyWasmSession", event: EventPayload):
            return handler(session, to_typed_event(event))

        self._event_handlers[(event_kind, widget_id)] = adapt_event_handler(_wrapped)

    def _resolve_widget_id(self, widget_or_id: WasmWidget | str) -> str:
        if isinstance(widget_or_id, WasmWidget):
            return widget_or_id.id
        return widget_or_id

    def connect(
        self,
        widget_or_id: WasmWidget | str,
        event_kind: str,
        handler: CompatibleEventHandler,
    ) -> None:
        self.register_event_handler(
            event_kind,
            self._resolve_widget_id(widget_or_id),
            handler,
        )

    def on_click(self, widget_or_id: WasmWidget | str, handler: CompatibleEventHandler) -> None:
        self.connect(widget_or_id, "click", handler)

    def on_change(self, widget_or_id: WasmWidget | str, handler: CompatibleEventHandler) -> None:
        self.connect(widget_or_id, "change", handler)

    def on_click_typed(self, widget_or_id: WasmWidget | str, handler: CompatibleEventHandler) -> None:
        self.register_typed_event_handler(
            "click",
            self._resolve_widget_id(widget_or_id),
            handler,
        )

    def on_change_typed(self, widget_or_id: WasmWidget | str, handler: CompatibleEventHandler) -> None:
        self.register_typed_event_handler(
            "change",
            self._resolve_widget_id(widget_or_id),
            handler,
        )

    def widget(self, widget_id: str) -> WasmWidget | None:
        return self._state.tree.get(widget_id)

    def create(self, widget: WasmWidget) -> OutgoingMessage:
        return self.message_create(widget)

    def create_many(self, widgets: Sequence[WasmWidget]) -> list[OutgoingMessage]:
        return [self.message_create(widget) for widget in widgets]

    def create_component(self, component: Any) -> list[OutgoingMessage]:
        widgets = render_component_widgets(component, self)
        return self.create_many(widgets)

    def delete(self, widget_or_id: WasmWidget | str) -> OutgoingMessage:
        return self.message_delete(self._resolve_widget_id(widget_or_id))

    def update(self, widget_or_id: WasmWidget | str, **patch: Any) -> OutgoingMessage:
        return self.message_update(self._resolve_widget_id(widget_or_id), patch)

    def set_default_event_handler(self, handler: CompatibleEventHandler) -> None:
        self._default_handler = adapt_event_handler(handler)

    def set_default_style_for_kind(
        self,
        kind: str,
        style: Style | dict[str, Any] | str | None = None,
        **properties: Any,
    ) -> None:
        normalized = self._merge_style_inputs(style, properties)
        if not normalized:
            self._default_style_by_kind.pop(kind, None)
            return
        self._default_style_by_kind[kind] = normalized

    def set_default_style_for_class(
        self,
        class_name: str,
        style: Style | dict[str, Any] | str | None = None,
        **properties: Any,
    ) -> None:
        normalized = self._merge_style_inputs(style, properties)
        if not normalized:
            self._default_style_by_class.pop(class_name, None)
            return
        self._default_style_by_class[class_name] = normalized

    def clear_default_styles(self) -> None:
        self._default_style_by_kind.clear()
        self._default_style_by_class.clear()

    def message_update(self, widget_id: str, patch: dict[str, Any]) -> OutgoingMessage:
        full_patch = {"id": widget_id, **patch}
        self._apply_patch_to_tree(widget_id, patch)
        return OutgoingMessage(type="update", patch=full_patch)

    def message_create(self, widget: WasmWidget) -> OutgoingMessage:
        detached = self._clone_widget(widget)
        self._apply_style_defaults(detached)
        self._state.tree.upsert(detached)
        self._register_widget_handlers(detached)
        payload = self._state.tree.as_payload(detached.id)
        if payload is None:
            raise ValueError(f"widget not found: {detached.id}")
        return OutgoingMessage(type="create", widget=WidgetPayload(**payload))

    def _clone_widget(self, widget: WasmWidget) -> WasmWidget:
        return widget.clone()

    def _register_widget_handlers(self, widget: WasmWidget) -> None:
        for event_kind, handler in widget.iter_event_handlers():
            self.register_event_handler(event_kind, widget.id, handler)

    def _merge_style_inputs(
        self,
        style: Style | dict[str, Any] | str | None,
        properties: dict[str, Any],
    ) -> dict[str, str]:
        base = style_dict(style) or {}
        extra = style_dict(properties) if properties else None
        if extra:
            return {**base, **extra}
        return base

    def _apply_style_defaults(self, widget: WasmWidget) -> None:
        merged_defaults: dict[str, str] = {}

        kind_defaults = self._default_style_by_kind.get(widget.kind)
        if kind_defaults:
            merged_defaults.update(kind_defaults)

        classes = widget.props.get("classes")
        if isinstance(classes, list):
            for class_name in classes:
                if not isinstance(class_name, str):
                    continue
                class_defaults = self._default_style_by_class.get(class_name)
                if class_defaults:
                    merged_defaults.update(class_defaults)

        if not merged_defaults:
            return

        existing_style = style_dict(widget.props.get("style")) or {}
        widget.props["style"] = {**merged_defaults, **existing_style}

    def message_delete(self, widget_id: str) -> OutgoingMessage:
        return OutgoingMessage(
            type="delete",
            widget=WidgetPayload(
                id=widget_id,
                kind="Unknown",
                parent="root",
                props={},
                children=[],
            ),
        )

    def serialize(self, msg: OutgoingMessage) -> str:
        return msg.model_dump_json(exclude_none=True)

    def _record_command(self, raw: str) -> None:
        try:
            parsed = OutgoingMessage.model_validate_json(raw)
        except ValidationError:
            return
        if parsed.type in {"create", "update", "delete"}:
            self._replay_commands.append(raw)

    def _apply_patch_to_tree(self, widget_id: str, patch: dict[str, Any]) -> None:
        widget = self._state.tree.get(widget_id)
        if widget is None:
            return

        for key in ("text", "value", "enabled", "classes"):
            if key in patch:
                widget.props[key] = patch[key]

        style_patch = patch.get("style")
        if isinstance(style_patch, dict):
            widget.props.setdefault("style", {})
            current_style = widget.props.get("style")
            if isinstance(current_style, dict):
                for style_name, style_value in style_patch.items():
                    if style_value is None:
                        current_style.pop(style_name, None)
                    else:
                        current_style[style_name] = style_value

        attrs = patch.get("attrs")
        if isinstance(attrs, dict):
            widget.props.setdefault("attrs", {})
            current_attrs = widget.props.get("attrs")
            if isinstance(current_attrs, dict):
                current_attrs.update(attrs)

        remove_attrs = patch.get("remove_attrs")
        if isinstance(remove_attrs, list):
            current_attrs = widget.props.get("attrs")
            if isinstance(current_attrs, dict):
                for attr_name in remove_attrs:
                    if isinstance(attr_name, str):
                        current_attrs.pop(attr_name, None)

    def _normalize_callback_responses(
        self,
        produced: list[CallbackResponse] | CallbackResponse,
    ) -> list[str]:
        items = produced if isinstance(produced, list) else [produced]
        out: list[str] = []
        for item in items:
            if item is None:
                continue
            if isinstance(item, str):
                out.append(item)
                self._record_command(item)
                continue
            if isinstance(item, OutgoingMessage):
                serialized = self.serialize(item)
                out.append(serialized)
                self._record_command(serialized)
                continue
            if isinstance(item, dict):
                if "type" in item:
                    serialized = self.serialize(OutgoingMessage(**item))
                    out.append(serialized)
                    self._record_command(serialized)
                else:
                    widget_id = item.get("id")
                    if not isinstance(widget_id, str):
                        continue
                    patch = {k: v for k, v in item.items() if k != "id"}
                    serialized = self.serialize(self.message_update(widget_id, patch))
                    out.append(serialized)
                    self._record_command(serialized)
        return out

    def _acknowledgement_message(self, nonce: int | None) -> str | None:
        if nonce is None:
            return None
        return OutgoingMessage(
            type="ack",
            meta={"nonce": nonce, "status": "processed"},
        ).model_dump_json(exclude_none=True)

    def _append_acknowledgement(self, responses: list[str], nonce: int | None) -> list[str]:
        ack = self._acknowledgement_message(nonce)
        if ack is None:
            return responses
        return [*responses, ack]

    def _with_command_id(self, raw: str) -> str:
        try:
            outgoing = OutgoingMessage.model_validate_json(raw)
        except ValidationError:
            return raw

        if outgoing.type not in {"create", "update", "delete"}:
            return raw

        meta = dict(outgoing.meta or {})
        command_id = meta.get("command_id")
        if not isinstance(command_id, str) or len(command_id) == 0:
            command_id = uuid.uuid4().hex
            meta["command_id"] = command_id
            outgoing.meta = meta
            raw = outgoing.model_dump_json(exclude_none=True)

        self._pending_outbound_command_ids.add(command_id)
        return raw

    def prepare_outbound_commands(self, raw_commands: Sequence[str]) -> list[str]:
        return [self._with_command_id(raw) for raw in raw_commands]

    def _handle_receipt_message(self, raw: str) -> list[str]:
        try:
            incoming = ReceiptMessage.model_validate_json(raw)
        except ValidationError as exc:
            raise ProtocolViolationError("invalid-json-schema", close_code=1003) from exc

        sec = self._security.validate_session_token(incoming.session.token)
        if sec is None:
            raise ProtocolViolationError("invalid-session")

        self._pending_outbound_command_ids.discard(incoming.receipt.command_id)
        return []

    @staticmethod
    def _normalize_incoming_value(value: Any) -> Any:
        normalized: Any = value
        if isinstance(value, list):
            normalized = [PyWasmSession._normalize_incoming_value(item) for item in value]
        elif isinstance(value, dict):
            normalized = {
                str(key): PyWasmSession._normalize_incoming_value(item)
                for key, item in value.items()
            }
        elif isinstance(value, str):
            raw = value.strip()
            lowered = raw.lower()
            if lowered == "true":
                normalized = True
            elif lowered == "false":
                normalized = False
            elif lowered == "null":
                normalized = None
            elif re.fullmatch(r"-?(0|[1-9]\d*)", raw):
                try:
                    normalized = int(raw)
                except ValueError:
                    normalized = value
            elif re.fullmatch(r"-?(0|[1-9]\d*)\.\d+", raw):
                try:
                    normalized = float(raw)
                except ValueError:
                    normalized = value
        return normalized

    def bootstrap_messages(self) -> list[str]:
        out: list[str] = []
        out.append(
            OutgoingMessage(
                type="init",
                session=SessionRef(token=self._state.security.session_token),
                client_secret=self._state.security.client_secret,
            ).model_dump_json(exclude_none=True)
        )

        if self._bootstrapped:
            out.extend(self._replay_commands)
            return out

        for widget in self._initial_widgets:
            detached = self._clone_widget(widget)
            self._apply_style_defaults(detached)
            self._state.tree.upsert(detached)
            self._register_widget_handlers(detached)
            payload = self._state.tree.as_payload(detached.id)
            if payload is None:
                continue
            create_raw = OutgoingMessage(
                type="create",
                widget=WidgetPayload(**payload),
                meta={"timestamp": 1710000000},
            ).model_dump_json(exclude_none=True)
            out.append(create_raw)
            self._record_command(create_raw)

        self._bootstrapped = True

        return out

    def handle_client_message(self, raw: str) -> list[str]:
        try:
            frame = json.loads(raw)
        except (TypeError, ValueError):
            frame = None

        if isinstance(frame, dict) and frame.get("type") == "receipt":
            return self._handle_receipt_message(raw)

        try:
            incoming = EventMessage.model_validate_json(raw)
        except ValidationError as exc:
            raise ProtocolViolationError("invalid-json-schema", close_code=1003) from exc

        sec = self._security.validate_session_token(incoming.session.token)
        if sec is None:
            raise ProtocolViolationError("invalid-session")

        # Wrapper mode: accept raw events without client-side signature.
        if incoming.mac is not None:
            event_dict = incoming.event.model_dump()
            if not self._security.verify_event_hmac(sec, event_dict, incoming.mac):
                raise ProtocolViolationError("invalid-mac")
            if incoming.event.nonce is None:
                raise ProtocolViolationError("invalid-nonce")
            if not self._security.verify_nonce(sec, incoming.event.nonce):
                raise ProtocolViolationError("invalid-nonce")

        incoming.event.value = self._normalize_incoming_value(incoming.event.value)

        handler = self._event_handlers.get((incoming.event.kind, incoming.event.id))
        if handler is not None:
            responses = self._normalize_callback_responses(handler(self, incoming.event))
            return self._append_acknowledgement(responses, incoming.event.nonce)

        if self._default_handler is not None:
            responses = self._normalize_callback_responses(
                self._default_handler(self, incoming.event)
            )
            return self._append_acknowledgement(responses, incoming.event.nonce)

        if incoming.event.kind == "click" and incoming.event.id == "btn1":
            patch = {"id": "label1", "text": "Bouton clique"}
            raw = OutgoingMessage(type="update", patch=patch).model_dump_json(exclude_none=True)
            self._record_command(raw)
            self._apply_patch_to_tree("label1", {"text": "Bouton clique"})
            return self._append_acknowledgement([raw], incoming.event.nonce)

        return self._append_acknowledgement([], incoming.event.nonce)
