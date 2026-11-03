import logging

import httpx

from ups_kulka.modules.notifications.application.ports import MessageSender

logger = logging.getLogger("ups_kulka.notifications")

TELEGRAM_API = "https://api.telegram.org"


class TelegramSender:
    """Sends to one chat. The recipient changes via UPS_TELEGRAM_CHAT_ID, not code."""

    def __init__(self, bot_token: str, chat_id: str, timeout: float = 5.0) -> None:
        self._url = f"{TELEGRAM_API}/bot{bot_token}/sendMessage"
        self._chat_id = chat_id
        self._timeout = timeout

    async def send(self, text: str) -> None:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(self._url, json={"chat_id": self._chat_id, "text": text})
            response.raise_for_status()


class LogSender:
    """Local development: no bot configured, messages go to the log."""

    async def send(self, text: str) -> None:
        logger.info("shop notification:\n%s", text)


def make_sender(bot_token: str, chat_id: str) -> MessageSender:
    if bot_token and chat_id:
        return TelegramSender(bot_token, chat_id)
    return LogSender()
