from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from typing import Optional

from .models import Message
from .telegram_client import TelegramFetcher


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    async def process_messages(self, limit: Optional[int] = None):
        """Process and store messages from Telegram channel."""
        async with TelegramFetcher() as fetcher:
            async for telegram_msg in fetcher.fetch_messages(limit):
                try:
                    # Download media if present
                    media_path = await fetcher.download_media(telegram_msg)
                    
                    # Create database record
                    message = Message(
                        message_id=telegram_msg.id,
                        date=telegram_msg.date,
                        chat_id=telegram_msg.chat_id,
                        sender_id=telegram_msg.sender_id,
                        text=telegram_msg.text,
                        media_path=str(media_path) if media_path else None
                    )
                    
                    self.db.merge(message)
                    await self.db.commit()
                    
                    logger.info(f"Processed message {telegram_msg.id}")
                    
                except Exception as e:
                    logger.error(f"Error processing message {telegram_msg.id}: {e}")
                    await self.db.rollback()
                    continue

    def get_messages(self, skip: int = 0, limit: int = 100):
        """Retrieve stored messages from the database."""
        return self.db.query(Message).offset(skip).limit(limit).all()

    def get_message(self, message_id: int):
        """Retrieve a specific message by its Telegram message ID."""
        return self.db.query(Message).filter(Message.message_id == message_id).first() 