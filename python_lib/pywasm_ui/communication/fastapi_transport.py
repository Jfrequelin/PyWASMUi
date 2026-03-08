from __future__ import annotations

from collections.abc import AsyncIterator
from asyncio import CancelledError


class FastAPIWasmCommandSender:
    def __init__(self, websocket: object) -> None:
        self._websocket = websocket

    async def send_command(self, message: str) -> None:
        await self._websocket.send_text(message)  # type: ignore[attr-defined]


class FastAPIWasmAsyncReceiver:
    def __init__(self, websocket: object) -> None:
        self._websocket = websocket

    async def iter_events(self) -> AsyncIterator[str]:
        while True:
            try:
                payload = await self._websocket.receive_text()  # type: ignore[attr-defined]
            except (RuntimeError, CancelledError):
                return
            yield payload
