import asyncio
import socks

from bd.database import Database
from bot.notify.notifybot import NotifyBot

from router import bot
from properties.config import TELETHON_ID, TELETHON_HASH, TELETHON_CHANNELS, DATABASE_PATH

from telethon import TelegramClient, events


class ChannelListener:
    def __init__(self, channels: list[int]):
        self._client = TelegramClient("account", TELETHON_ID, TELETHON_HASH)
        self._db = Database(DATABASE_PATH)
        self._notify = NotifyBot(bot, self._db)
        self._channels = channels

        @self._client.on(events.NewMessage(chats=self._channels))
        async def handler_new_message(event: events.NewMessage.Event):
                try:
                    userID = int(event.message.text)
                except:
                    return
                await self.register_user(userID)

    async def register_user(self, tgID: int):
        if await self._db.register_user(tgID):
            await self._notify.onUserRegistered(tgID)

    async def start(self) -> None:
        await self._db.connect()
        await self._client.start()
        await self._client.run_until_disconnected()


async def main():
    client = ChannelListener(TELETHON_CHANNELS)
    await client.start()


if __name__ == '__main__':
    asyncio.run(main())
