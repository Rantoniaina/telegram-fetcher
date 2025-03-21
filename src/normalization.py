import re
import time
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from typing import List, Optional

from .models import Message, NormalizedMessage


class NormalizationService:
    def __init__(self, db: Session):
        self.db = db

    def clean_message(self, text: Optional[str]) -> str:
        """Clean and normalize message text.

        Args:
            text: The text to clean and normalize

        Returns:
            Cleaned and normalized text string
        """
        if not isinstance(text, str):
            logger.warning("Received non-string text for cleaning, returning empty string")
            return ""  # Handle null values

        logger.debug(f"Starting text cleaning process. Original length: {len(text)}")
        text = text.lower()
        text = re.sub(r"http\S+|www\S+|#\S+", "", text)  # Remove URLs and hashtags
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters including punctuation
        text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
        logger.debug(f"Text cleaning completed. Final length: {len(text)}")
        return text

    def normalize_message(self, message: Message) -> bool:
        """Normalize a single message and store the result.

        Args:
            message: Message object to normalize

        Returns:
            bool: True if normalization was successful, False otherwise
        """
        try:
            logger.info(f"Starting normalization for message {message.id}")
            normalized_text = self.clean_message(message.text)
            
            # Skip saving if normalized text is empty
            if not normalized_text:
                message.is_normalized = True
                self.db.commit()
                logger.info(f"Skipped empty message {message.id}")
                return True
            
            # Create normalized message record
            normalized_msg = NormalizedMessage(
                original_message_id=message.id,
                normalized_text=normalized_text
            )
            
            # Update original message status
            message.is_normalized = True
            
            # Save changes
            self.db.add(normalized_msg)
            self.db.commit()
            
            logger.info(f"Successfully normalized message {message.id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error normalizing message {message.id}: {e}")
            return False

    def normalize_messages(self, batch_size: int = 100, skip_empty: bool = False) -> int:
        """Normalize all unnormalized messages in batches.

        Args:
            batch_size: Number of messages to process in each batch
            skip_empty: Skip messages with empty text

        Returns:
            Number of successfully normalized messages
        """
        logger.info(f"Starting batch normalization with batch size: {batch_size}")
        normalized_count = 0
        offset = 0
        batch_number = 0
        
        while True:
            batch_number += 1
            logger.info(f"Processing batch {batch_number} (offset: {offset})")
            
            # Get batch of unnormalized messages
            messages = self.db.query(Message)\
                .filter(Message.is_normalized == False)\
                .offset(offset)\
                .limit(batch_size)\
                .all()
            
            if not messages:
                logger.info("No more messages to normalize")
                break
                
            logger.info(f"Found {len(messages)} messages in batch {batch_number}")
            
            # Process batch
            batch_success = 0
            for message in messages:
                if skip_empty and (not message.text or message.text.strip() == ""):
                    message.is_normalized = True
                    self.db.commit()
                    batch_success += 1
                    continue
                    
                if self.normalize_message(message):
                    if message.text and message.text.strip():
                        normalized_count += 1
                    batch_success += 1
            
            logger.info(f"Batch {batch_number} completed. Success: {batch_success}/{len(messages)}")
            offset += batch_size
            
            # Add delay between batches to avoid database overload
            if len(messages) == batch_size:
                logger.info("Sleeping for 1 second before next batch")
                time.sleep(1)
        
        logger.info(f"Normalization completed. Total normalized: {normalized_count}")
        return normalized_count