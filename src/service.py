from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from typing import Optional, Callable
from telethon.tl.types import Message as TelegramMessage

from .models import Message, MediaFile
from .telegram_client import TelegramFetcher


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    async def process_messages(
        self,
        limit: Optional[int] = None,
        download_media: bool = True,
        keywords: Optional[list[str]] = None,
        date: Optional[str] = None,
        progress_callback: Optional[Callable[[TelegramMessage, int, int], None]] = None
    ):
        """
        Process and store messages from Telegram channel.
        
        Args:
            limit: Maximum number of messages to fetch
            download_media: Whether to download media files
            keywords: Optional list of keywords to filter messages
            date: Optional date string in format dd-MM-yyyy to filter messages
            progress_callback: Optional callback function to report progress
        """
        message_count = 0
        total_messages = 0
        
        # Parse date string if provided
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, "%d-%m-%Y").date()
            except ValueError as e:
                logger.error(f"Invalid date format: {e}. Expected format: dd-MM-yyyy")
                return
        
        async with TelegramFetcher() as fetcher:
            async for telegram_msg in fetcher.fetch_messages(limit):
                try:
                    # Skip messages not from target date if date filter is active
                    if target_date and telegram_msg.date.date() != target_date:
                        continue
                        
                    message_count += 1
                    if total_messages == 0:
                        # Get total on first message
                        total_messages = telegram_msg.chat.participants_count if hasattr(telegram_msg.chat, 'participants_count') else message_count
                    
                    # Report progress if callback is provided
                    if progress_callback:
                        progress_callback(telegram_msg, message_count, total_messages)
                    
                    # Create or update database record
                    message = Message(
                        message_id=telegram_msg.id,
                        date=telegram_msg.date,
                        chat_id=telegram_msg.chat_id,
                        sender_id=telegram_msg.sender_id,
                        text=telegram_msg.text
                    )
                    
                    try:
                        # Save message to get its ID
                        message = self.db.merge(message)
                        self.db.flush()
                    except Exception as db_error:
                        self.db.rollback()
                        logger.error(f"Database error for message {telegram_msg.id}: {db_error}")
                        continue
                    
                    # Check if message matches keywords first if provided
                    matches_keywords = True
                    if keywords:
                        message_text = (telegram_msg.text or "").lower()
                        matches_keywords = any(keyword.lower() in message_text for keyword in keywords)
                    
                    # Check if media download is enabled and media exists
                    should_download = download_media and telegram_msg.media
                    
                    # Download media if enabled and either no keywords are provided or message matches keywords
                    if should_download and (not keywords or matches_keywords):
                        media_path = await fetcher.download_media(telegram_msg)
                        if media_path:
                            # Create media file record
                            try:
                                media_file = MediaFile(
                                    message_id=message.id,
                                    file_path=str(media_path),
                                    file_type=type(telegram_msg.media).__name__
                                )
                                media_file = self.db.merge(media_file)
                            except Exception as db_error:
                                self.db.rollback()
                                logger.error(f"Database error for media file of message {telegram_msg.id}: {db_error}")
                                continue
                    
                    # Synchronous database operations
                    try:
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