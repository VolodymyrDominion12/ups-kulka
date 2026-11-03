"""Print the chat id to put into UPS_TELEGRAM_CHAT_ID (specs/008-notifications).

Telegram bots cannot write to a phone number. Steps:
  1. Create a bot with @BotFather, put its token into UPS_TELEGRAM_BOT_TOKEN.
  2. On the phone that should get orders, open the bot and press Start.
  3. uv run python scripts/telegram_chat_id.py
"""

import sys

import httpx

from ups_kulka.settings import Settings


def main() -> int:
    token = Settings().telegram_bot_token
    if not token:
        sys.stderr.write("Set UPS_TELEGRAM_BOT_TOKEN in backend/.env first\n")
        return 1
    response = httpx.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=10)
    response.raise_for_status()
    chats: dict[int, str] = {}
    for update in response.json().get("result", []):
        message = update.get("message") or update.get("my_chat_member") or {}
        chat = message.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("first_name") or chat.get("title") or ""
    if not chats:
        sys.stderr.write("No messages yet: open the bot in Telegram, press Start, run again\n")
        return 1
    for chat_id, name in chats.items():
        sys.stdout.write(f"UPS_TELEGRAM_CHAT_ID={chat_id}  # {name}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
