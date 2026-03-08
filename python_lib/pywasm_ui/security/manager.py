from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, field
from typing import Any

from .state import SessionSecurityState


@dataclass
class SecurityManager:
    server_secret: bytes
    sessions: dict[str, SessionSecurityState] = field(default_factory=dict)

    def create_session(self) -> SessionSecurityState:
        session_id = secrets.token_urlsafe(18)
        signature = hmac.new(
            self.server_secret,
            session_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        session_token = f"{session_id}.{signature}"
        client_secret = secrets.token_urlsafe(32)
        state = SessionSecurityState(
            session_id=session_id,
            session_token=session_token,
            client_secret=client_secret,
            last_nonce=0,
        )
        self.sessions[session_token] = state
        return state

    def validate_session_token(self, token: str) -> SessionSecurityState | None:
        state = self.sessions.get(token)
        if state is None:
            return None
        try:
            session_id, signature = token.split(".", 1)
        except ValueError:
            return None
        expected = hmac.new(
            self.server_secret,
            session_id.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        return state

    def canonical_event_json(self, event: dict[str, Any]) -> str:
        canonical = {
            "kind": event.get("kind"),
            "id": event.get("id"),
            "value": event.get("value"),
            "nonce": event.get("nonce"),
        }
        return json.dumps(canonical, separators=(",", ":"), ensure_ascii=False)

    def verify_event_hmac(
        self,
        state: SessionSecurityState,
        event: dict[str, Any],
        mac_b64: str,
    ) -> bool:
        try:
            mac_raw = base64.b64decode(mac_b64, validate=True)
        except (binascii.Error, ValueError):
            return False

        message = self.canonical_event_json(event).encode("utf-8")
        expected = hmac.new(
            state.client_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).digest()
        return hmac.compare_digest(mac_raw, expected)

    def verify_nonce(self, state: SessionSecurityState, nonce: int) -> bool:
        if nonce <= state.last_nonce:
            return False
        state.last_nonce = nonce
        return True
