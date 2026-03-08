from __future__ import annotations

from collections.abc import AsyncIterator

from .protocols import WasmAsyncEventReceiver, WasmCommandSender


class WasmAppCommunication:
    def __init__(self, sender: WasmCommandSender, receiver: WasmAsyncEventReceiver) -> None:
        self._sender = sender
        self._receiver = receiver

    async def send_commands(self, messages: list[str]) -> None:
        for message in messages:
            await self._sender.send_command(message)

    async def receive_events(self) -> AsyncIterator[str]:
        async for event in self._receiver.iter_events():
            yield event
