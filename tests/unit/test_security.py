from __future__ import annotations

import base64
import hashlib
import hmac

from pywasm_ui.security import SecurityManager


def _sign(secret: str, canonical_json: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        canonical_json.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def test_create_and_validate_session_token() -> None:
    manager = SecurityManager(server_secret=b"test-server-secret")
    session = manager.create_session()

    validated = manager.validate_session_token(session.session_token)

    assert validated is not None
    assert validated.session_id == session.session_id


def test_verify_event_hmac_accepts_valid_and_rejects_invalid() -> None:
    manager = SecurityManager(server_secret=b"test-server-secret")
    session = manager.create_session()

    event = {"kind": "click", "id": "btn1", "value": None, "nonce": 1}
    canonical = manager.canonical_event_json(event)
    valid_mac = _sign(session.client_secret, canonical)

    assert manager.verify_event_hmac(session, event, valid_mac)
    assert not manager.verify_event_hmac(session, event, "not-base64")


def test_verify_nonce_is_monotonic() -> None:
    manager = SecurityManager(server_secret=b"test-server-secret")
    session = manager.create_session()

    assert manager.verify_nonce(session, 1)
    assert manager.verify_nonce(session, 2)
    assert not manager.verify_nonce(session, 2)
    assert not manager.verify_nonce(session, 1)
