from telethon.sync import TelegramClient
from telethon.tl.types import Message as TelegramMessage
from telethon.errors import FloodWaitError
from pathlib import Path
from loguru import logger
from typing import Optional, Generator, AsyncGenerator
import asyncio

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

    async def fetch_messages(self, limit: Optional[int] = None) -> AsyncGenerator[TelegramMessage, None]:
        """Fetch messages from the configured channel."""
        try:
            logger.info(f"Connecting to channel: {settings.CHANNEL_NAME}")
            channel = await self.client.get_entity(settings.CHANNEL_NAME)
            logger.info(f"Successfully connected to channel: {channel.title}")
            
            # Get total message count first
            messages = await self.client.get_messages(channel, limit=0)
            total_messages = messages.total
            logger.info(f"Found {total_messages} messages in total")
            
            # Now fetch the actual messages
            fetch_limit = limit if limit else total_messages
            logger.info(f"Will fetch {fetch_limit} messages")
            
            messages = await self.client.get_messages(channel, limit=fetch_limit)
            message_count = 0
            for msg in messages:
                try:
                    message_count += 1
                    # Add a small delay between messages to avoid rate limits
                    await asyncio.sleep(1)
                    
                    # Add longer sleep every 100 messages
                    if message_count % 100 == 0:
                        logger.info("Sleeping for 10 seconds to avoid rate limit.")
                        await asyncio.sleep(10)
                        
                    yield msg
                except FloodWaitError as e:
                    logger.warning(f"Rate limit hit! Sleeping for {e.seconds} seconds")
                    await asyncio.sleep(e.seconds)
                    # Retry after waiting
                    yield msg
                
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            raise

    async def download_media(self, message: TelegramMessage) -> Optional[Path]:
        """Download media from a message if it exists with rate limiting."""
        if not message.media:
            return None

        try:
            # Add delay between downloads to avoid rate limits
            await asyncio.sleep(2)
            
            file_path = self.media_path / str(message.id)
            downloaded_path = await message.download_media(file=file_path)
            
            if downloaded_path:
                logger.info(f"Successfully downloaded media for message {message.id}")
                return Path(downloaded_path)
            else:
                logger.warning(f"No media downloaded for message {message.id}")
                return None
                
        except FloodWaitError as e:
            logger.warning(f"Rate limit hit while downloading media! Sleeping for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            # Retry download after waiting
            return await self.download_media(message)
        except Exception as e:
            logger.error(f"Error downloading media for message {message.id}: {e}")
            return None