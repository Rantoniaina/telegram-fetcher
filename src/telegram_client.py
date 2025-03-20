from telethon.sync import TelegramClient
from telethon.tl.types import Message as TelegramMessage
from pathlib import Path
from loguru import logger
from typing import Optional, Generator

from .config import settings


class TelegramFetcher:
    def __init__(self):
        self.client = TelegramClient(
            settings.SESSION_NAME,
            settings.API_ID,
            settings.API_HASH
        )
        self.media_path = settings.MEDIA_PATH
        self.media_path.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        await self.client.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()

    async def fetch_messages(self, limit: Optional[int] = None) -> Generator[TelegramMessage, None, None]:
        """Fetch messages from the configured channel."""
        try:
            messages = await self.client.get_messages(settings.CHANNEL_NAME, limit=limit)
            for msg in messages:
                yield msg
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            raise

    async def download_media(self, message: TelegramMessage) -> Optional[Path]:
        """Download media from a message if it exists."""
        if not message.media:
            return None

        try:
            file_path = self.media_path / str(message.id)
            downloaded_path = await message.download_media(file=file_path)
            return Path(downloaded_path) if downloaded_path else None
        except Exception as e:
            logger.error(f"Error downloading media for message {message.id}: {e}")
            return None 