from __future__ import annotations


class ProtocolViolationError(Exception):
    def __init__(self, reason: str, close_code: int = 1008) -> None:
        super().__init__(reason)
        self.reason = reason
        self.close_code = close_code
