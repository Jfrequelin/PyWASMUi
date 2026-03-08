from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SessionSecurityState:
    session_id: str
    session_token: str
    client_secret: str
    last_nonce: int = 0
