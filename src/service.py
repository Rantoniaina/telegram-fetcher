from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from typing import Optional, Callable
from telethon.tl.types import Message as TelegramMessage

from .models import Message
from .telegram_client import TelegramFetcher


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    async def process_messages(
        self,
        limit: Optional[int] = None,
        download_media: bool = True,
        progress_callback: Optional[Callable[[TelegramMessage, int, int], None]] = None
    ):
        """
        Process and store messages from Telegram channel.
        
        Args:
            limit: Maximum number of messages to fetch
            download_media: Whether to download media files
            progress_callback: Optional callback function to report progress
        """
        message_count = 0
        total_messages = 0
        
        async with TelegramFetcher() as fetcher:
            async for telegram_msg in fetcher.fetch_messages(limit):
                try:
                    message_count += 1
                    if total_messages == 0:
                        # Get total on first message
                        total_messages = telegram_msg.chat.participants_count if hasattr(telegram_msg.chat, 'participants_count') else message_count
                    
                    # Report progress if callback is provided
                    if progress_callback:
                        progress_callback(telegram_msg, message_count, total_messages)
                    
                    # Create database record first
                    message = Message(
                        message_id=telegram_msg.id,
                        date=telegram_msg.date,
                        chat_id=telegram_msg.chat_id,
                        sender_id=telegram_msg.sender_id,
                        text=telegram_msg.text
                    )
                    
                    # Save message to get its ID
                    self.db.add(message)
                    self.db.flush()
                    
                    # Download media if present and enabled
                    if download_media and telegram_msg.media:
                        media_path = await fetcher.download_media(telegram_msg)
                        if media_path:
                            # Create media file record
                            media_file = MediaFile(
                                message_id=message.id,
                                file_path=str(media_path),
                                file_type=type(telegram_msg.media).__name__
                            )
                            self.db.add(media_file)
                    
                    # Synchronous database operations
                    try:
                        self.db.merge(message)
                        self.db.commit()
                    except Exception as db_error:
                        self.db.rollback()
                        logger.error(f"Database error for message {telegram_msg.id}: {db_error}")
                        continue
                    
                    logger.info(f"Processed message {telegram_msg.id} ({message_count}/{total_messages})")
                    
                except Exception as e:
                    logger.error(f"Error processing message {telegram_msg.id}: {e}")
                    continue

    def get_messages(self, skip: int = 0, limit: int = 100):
        """Retrieve stored messages from the database."""
        return self.db.query(Message).offset(skip).limit(limit).all()

    def get_message(self, message_id: int):
        """Retrieve a specific message by its Telegram message ID."""
        return self.db.query(Message).filter(Message.message_id == message_id).first()

    def get_unnormalized_messages(self, skip: int = 0, limit: Optional[int] = None):
        """Retrieve messages that haven't been normalized yet.

        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return. If None, returns all messages.

        Returns:
            List of Message objects that haven't been normalized
        """
        query = self.db.query(Message).filter(Message.is_normalized == False)
        
        if skip:
            query = query.offset(skip)
        
        if limit is not None:
            query = query.limit(limit)
            
        return query.all()