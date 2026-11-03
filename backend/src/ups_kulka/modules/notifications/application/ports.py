from typing import Protocol


class MessageSender(Protocol):
    """Delivers a text to the shop (Telegram chat in production, log locally)."""

    async def send(self, text: str) -> None: ...
