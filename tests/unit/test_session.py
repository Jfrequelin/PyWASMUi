from __future__ import annotations

import base64
import hashlib
import hmac
import json

import pytest

from pywasm_ui.security import SecurityManager
from pywasm_ui.session import ProtocolViolationError, PyWasmSession
from pywasm_ui.protocol import OutgoingMessage
from pywasm_ui.widgets import ButtonWidget, LabelWidget


def _sign(secret: str, event: dict[str, object]) -> str:
    canonical = json.dumps(
        {
            "kind": event["kind"],
            "id": event["id"],
            "value": event["value"],
            "nonce": event["nonce"],
        },
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def test_bootstrap_messages_include_init_and_creates() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))

    messages = [json.loads(msg) for msg in session.bootstrap_messages()]

    assert messages[0]["type"] == "init"
    assert any(msg["type"] == "create" and msg["widget"]["id"] == "label1" for msg in messages)
    assert any(msg["type"] == "create" and msg["widget"]["id"] == "btn1" for msg in messages)


def test_callback_handler_drives_update_patch() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    def on_click(current: PyWasmSession, _event: object) -> dict[str, str]:
        count = int(current.data.get("count", 0)) + 1
        current.data["count"] = count
        return {"id": "label1", "text": f"Count={count}"}

    session.register_event_handler("click", "btn1", on_click)

    event = {"kind": "click", "id": "btn1", "value": None, "nonce": 1}
    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": event,
        "mac": _sign(init["client_secret"], event),
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]

    assert responses[0]["type"] == "update"
    assert responses[0]["patch"]["id"] == "label1"
    assert responses[0]["patch"]["text"] == "Count=1"


def test_unsigned_event_is_accepted_in_wrapper_mode() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    event = {"kind": "click", "id": "btn1", "value": None}
    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": event,
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]

    assert responses[0]["type"] == "update"
    assert responses[0]["patch"]["id"] == "label1"


def test_invalid_mac_raises_protocol_violation() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    event = {"kind": "click", "id": "btn1", "value": None, "nonce": 1}
    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": event,
        "mac": "invalid-mac",
    }

    with pytest.raises(ProtocolViolationError, match="invalid-mac"):
        session.handle_client_message(json.dumps(payload))


def test_bootstrap_replays_previous_commands_after_session_started() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    event = {"kind": "click", "id": "btn1", "value": None}
    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": event,
    }

    first_responses = [
        json.loads(msg)
        for msg in session.handle_client_message(json.dumps(payload))
    ]
    assert first_responses[0]["type"] == "update"

    reconnect_bootstrap = [json.loads(msg) for msg in session.bootstrap_messages()]

    assert reconnect_bootstrap[0]["type"] == "init"
    assert any(
        msg["type"] == "update"
        and msg["patch"]["id"] == "label1"
        and msg["patch"]["text"] == "Bouton clique"
        for msg in reconnect_bootstrap
    )


def test_style_patch_is_replayed_on_reconnect_bootstrap() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    def on_click(_current: PyWasmSession, _event: object) -> dict[str, object]:
        return {"id": "label1", "style": {"font-size": "18px", "color": "#111111"}}

    session.register_event_handler("click", "btn1", on_click)

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {"kind": "click", "id": "btn1", "value": None},
    }
    session.handle_client_message(json.dumps(payload))

    reconnect_bootstrap = [json.loads(msg) for msg in session.bootstrap_messages()]
    style_updates = [
        msg
        for msg in reconnect_bootstrap
        if msg.get("type") == "update" and msg.get("patch", {}).get("id") == "label1"
    ]

    assert style_updates
    assert any(
        update["patch"].get("style", {}).get("font-size") == "18px"
        for update in style_updates
    )


def test_initial_widget_definitions_are_not_shared_between_sessions() -> None:
    security = SecurityManager(server_secret=b"test-server-secret")
    shared_initial_widgets = [LabelWidget(id="label1", parent="root", text="Default")]

    session1 = PyWasmSession(security_manager=security, initial_widgets=shared_initial_widgets)
    session1.bootstrap_messages()
    session1.message_update("label1", {"text": "Mutated"})

    session2 = PyWasmSession(security_manager=security, initial_widgets=shared_initial_widgets)
    boot2 = [json.loads(msg) for msg in session2.bootstrap_messages()]

    creates = [
        msg
        for msg in boot2
        if msg.get("type") == "create" and msg.get("widget", {}).get("id") == "label1"
    ]
    assert creates
    assert creates[0]["widget"]["props"]["text"] == "Default"


def test_session_widget_lookup_returns_manipulable_widget_object() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    session.bootstrap_messages()

    label = session.widget("label1")

    assert isinstance(label, LabelWidget)
    assert label.text() == "Pret"
    label.text("Updated from object")
    label.style.margin = "10px"

    assert label.text() == "Updated from object"
    assert label.style.margin == "10px"


def test_widget_on_click_callback_is_bound_during_creation() -> None:
    def on_click(current: PyWasmSession, _event: object) -> dict[str, str]:
        return {"id": "label1", "text": f"count={int(current.data.get('count', 0)) + 1}"}

    initial_widgets = [
        LabelWidget(id="label1", parent="root", text="Default"),
        ButtonWidget(id="btn_custom", parent="root", text="Go", on_click=on_click),
    ]

    session = PyWasmSession(
        SecurityManager(server_secret=b"test-server-secret"),
        initial_widgets=initial_widgets,
    )
    init = json.loads(session.bootstrap_messages()[0])

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {"kind": "click", "id": "btn_custom", "value": None},
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]

    assert responses[0]["type"] == "update"
    assert responses[0]["patch"]["id"] == "label1"
    assert responses[0]["patch"]["text"] == "count=1"


def test_message_create_registers_widget_bound_callbacks() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    def on_click(_current: PyWasmSession, _event: object) -> dict[str, str]:
        return {"id": "label1", "text": "Dynamic click"}

    created = ButtonWidget(id="btn_dynamic", parent="root", text="Dyn", on_click=on_click)
    session.message_create(created)

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {"kind": "click", "id": "btn_dynamic", "value": None},
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]

    assert responses[0]["type"] == "update"
    assert responses[0]["patch"]["text"] == "Dynamic click"


def test_event_processing_emits_ack_for_nonce() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {"kind": "click", "id": "btn1", "value": None, "nonce": 42},
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]

    assert responses[0]["type"] == "update"
    assert responses[-1]["type"] == "ack"
    assert responses[-1]["meta"]["nonce"] == 42
    assert responses[-1]["meta"]["status"] == "processed"


def test_session_pythonic_helpers_connect_and_manipulate_widgets() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    label = LabelWidget(id="label_helper", parent="root", text="0")
    button = ButtonWidget(id="btn_helper", parent="root", text="Inc")

    def on_click(current: PyWasmSession, _event: object) -> dict[str, str]:
        existing = current.widget("label_helper")
        assert existing is not None
        value = int(existing.text() or "0") + 1
        existing.text(str(value))
        return {"id": existing.id, "text": existing.text()}

    session.create(label)
    session.create(button)
    session.on_click(button, on_click)

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {"kind": "click", "id": "btn_helper", "value": None},
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]
    assert responses[0]["type"] == "update"
    assert responses[0]["patch"]["id"] == "label_helper"
    assert responses[0]["patch"]["text"] == "1"

    updated = session.update("label_helper", text="7")
    updated_payload = updated.model_dump()
    assert updated_payload["patch"] is not None
    assert updated_payload["patch"]["text"] == "7"

    deleted = session.delete(label)
    assert deleted.type == "delete"
    assert deleted.widget is not None
    assert deleted.widget.id == "label_helper"


def test_on_click_accepts_session_only_handler() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    session.create(LabelWidget(id="label_session_only", parent="root", text="0"))
    button = ButtonWidget(id="btn_session_only", parent="root", text="Go")
    session.create(button)

    def on_click(current: PyWasmSession) -> dict[str, str]:
        return {"id": "label_session_only", "text": str(int(current.data.get("n", 0)) + 1)}

    session.on_click(button, on_click)
    session.data["n"] = 0

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {"kind": "click", "id": "btn_session_only", "value": None},
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]
    assert responses[0]["type"] == "update"
    assert responses[0]["patch"]["text"] == "1"


def test_on_click_accepts_zero_arg_handler() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    session.create(LabelWidget(id="label_zero", parent="root", text="off"))
    button = ButtonWidget(id="btn_zero", parent="root", text="Toggle")
    session.create(button)

    def on_click() -> dict[str, str]:
        return {"id": "label_zero", "text": "on"}

    session.on_click(button, on_click)

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {"kind": "click", "id": "btn_zero", "value": None},
    }

    responses = [json.loads(msg) for msg in session.handle_client_message(json.dumps(payload))]
    assert responses[0]["type"] == "update"
    assert responses[0]["patch"]["text"] == "on"


def test_incoming_event_values_are_auto_coerced_for_handlers() -> None:
    session = PyWasmSession(SecurityManager(server_secret=b"test-server-secret"))
    init = json.loads(session.bootstrap_messages()[0])

    captured: dict[str, object] = {}

    def on_change(_current: PyWasmSession, event: object) -> dict[str, str]:
        captured["value"] = getattr(event, "value", None)
        return {"id": "label1", "text": "ok"}

    session.register_event_handler("change", "btn1", on_change)

    payload = {
        "protocol": 1,
        "type": "event",
        "session": {"token": init["session"]["token"]},
        "event": {
            "kind": "change",
            "id": "btn1",
            "value": "42",
        },
    }

    session.handle_client_message(json.dumps(payload))
    assert captured["value"] == 42


def test_outgoing_message_normalizes_non_json_values() -> None:
    message = OutgoingMessage(
        type="update",
        patch={
            "id": "label1",
            "tuple": (1, 2),
            "set": {"a", "b"},
            "obj": object(),
        },
    )

    payload = message.model_dump()
    assert payload["patch"] is not None
    assert isinstance(payload["patch"]["tuple"], list)
    assert isinstance(payload["patch"]["set"], list)
    assert isinstance(payload["patch"]["obj"], str)


def test_session_default_style_apis_apply_and_snapshot() -> None:
    session = PyWasmSession(
        SecurityManager(server_secret=b"test-server-secret"),
        initial_widgets=[ButtonWidget(id="btn1", parent="root", text="ok", classes=["primary"])],
    )

    session.set_default_style_for_kind("Button", "font-size: 13px")
    session.set_default_style_for_class("primary", {"padding": "8px"})

    boot = [json.loads(msg) for msg in session.bootstrap_messages()]
    create = next(m for m in boot if m.get("type") == "create" and m["widget"]["id"] == "btn1")
    assert create["widget"]["props"]["style"]["font-size"] == "13px"
    assert create["widget"]["props"]["style"]["padding"] == "8px"
