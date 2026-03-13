from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from server.app.examples.fastapi.fastapi_server import app


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


def _receive_non_ack(ws) -> dict[str, object]:
    while True:
        payload = json.loads(ws.receive_text())
        if payload.get("type") != "ack":
            return payload


def _patch(payload: dict[str, object]) -> dict[str, Any]:
    return cast(dict[str, Any], payload["patch"])


def test_websocket_flow_init_create_and_click_update() -> None:
    client = TestClient(app)

    with client.websocket_connect("/ws") as ws:
        init = json.loads(ws.receive_text())
        create_messages = [json.loads(ws.receive_text()) for _ in range(4)]

        assert init["type"] == "init"
        created_ids = {msg["widget"]["id"] for msg in create_messages}
        assert {"label1", "btn1", "label2", "btn2"}.issubset(created_ids)

        event = {"kind": "click", "id": "btn1", "value": None, "nonce": 1}
        ws.send_text(
            json.dumps(
                {
                    "protocol": 1,
                    "type": "event",
                    "session": {"token": init["session"]["token"]},
                    "event": event,
                    "mac": _sign(init["client_secret"], event),
                }
            )
        )

        update = _receive_non_ack(ws)
        update_patch = _patch(update)

        assert update["type"] == "update"
        assert update_patch["id"] == "label1"
        assert update_patch["text"] == "1"

        ws.send_text(
            json.dumps(
                {
                    "protocol": 1,
                    "type": "event",
                    "session": {"token": init["session"]["token"]},
                    "event": {"kind": "click", "id": "btn2", "value": None, "nonce": 2},
                    "mac": _sign(
                        init["client_secret"],
                        {"kind": "click", "id": "btn2", "value": None, "nonce": 2},
                    ),
                }
            )
        )
        second_update = _receive_non_ack(ws)
        second_update_patch = _patch(second_update)
        assert second_update_patch["id"] == "label2"
        assert second_update_patch["text"] == "2"


def test_websocket_replay_nonce_is_rejected() -> None:
    client = TestClient(app)

    with client.websocket_connect("/ws") as ws:
        init = json.loads(ws.receive_text())
        for _ in range(4):
            ws.receive_text()

        event = {"kind": "click", "id": "btn1", "value": None, "nonce": 7}
        signed = {
            "protocol": 1,
            "type": "event",
            "session": {"token": init["session"]["token"]},
            "event": event,
            "mac": _sign(init["client_secret"], event),
        }

        ws.send_text(json.dumps(signed))
        first_update = _receive_non_ack(ws)
        assert first_update["type"] == "update"

        # Replay exactly the same signed event: same nonce + same MAC.
        ws.send_text(json.dumps(signed))
        with pytest.raises(WebSocketDisconnect):
            while True:
                message = json.loads(ws.receive_text())
                if message.get("type") != "ack":
                    break


def test_websocket_refresh_keeps_session_state_with_session_token() -> None:
    client = TestClient(app)

    with client.websocket_connect("/ws") as ws:
        init = json.loads(ws.receive_text())
        for _ in range(4):
            ws.receive_text()

        ws.send_text(
            json.dumps(
                {
                    "protocol": 1,
                    "type": "event",
                    "session": {"token": init["session"]["token"]},
                    "event": {"kind": "click", "id": "btn1", "value": None, "nonce": 1},
                    "mac": _sign(
                        init["client_secret"],
                        {"kind": "click", "id": "btn1", "value": None, "nonce": 1},
                    ),
                }
            )
        )
        update = _receive_non_ack(ws)
        update_patch = _patch(update)
        assert update_patch["text"] == "1"

    token = init["session"]["token"]
    with client.websocket_connect(f"/ws?session_token={token}") as ws:
        reconnect_init = json.loads(ws.receive_text())
        replayed_messages = [json.loads(ws.receive_text()) for _ in range(5)]

        assert reconnect_init["session"]["token"] == token
        assert any(
            msg["type"] == "update"
            and msg["patch"]["id"] == "label1"
            and msg["patch"]["text"] == "1"
            for msg in replayed_messages
        )

        ws.send_text(
            json.dumps(
                {
                    "protocol": 1,
                    "type": "event",
                    "session": {"token": token},
                    "event": {"kind": "click", "id": "btn1", "value": None, "nonce": 2},
                    "mac": _sign(
                        reconnect_init["client_secret"],
                        {"kind": "click", "id": "btn1", "value": None, "nonce": 2},
                    ),
                }
            )
        )
        second_update = _receive_non_ack(ws)
        second_update_patch = _patch(second_update)
        assert second_update_patch["text"] == "2"


def test_websocket_accepts_receipt_for_server_command() -> None:
    client = TestClient(app)

    with client.websocket_connect("/ws") as ws:
        init = json.loads(ws.receive_text())
        first_server_command = json.loads(ws.receive_text())
        command_id = first_server_command.get("meta", {}).get("command_id")

        assert isinstance(command_id, str)

        ws.send_text(
            json.dumps(
                {
                    "protocol": 1,
                    "type": "receipt",
                    "session": {"token": init["session"]["token"]},
                    "receipt": {"command_id": command_id, "status": "received"},
                }
            )
        )

        # Endpoint should keep the socket open after receipt.
        remaining = [json.loads(ws.receive_text()) for _ in range(3)]
        assert all(msg["type"] == "create" for msg in remaining)
