from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol


class WasmCommandSender(Protocol):
    async def send_command(self, message: str) -> None:
        ...


class WasmAsyncEventReceiver(Protocol):
    def iter_events(self) -> AsyncIterator[str]:
        ...
