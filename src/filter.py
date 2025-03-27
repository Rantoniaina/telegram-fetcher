from loguru import logger
from sqlalchemy.orm import Session
from typing import List

from .models import Message, NormalizedMessage, FilteredMessage


class FilterService:
    def __init__(self, db: Session):
        self.db = db

    def filter_message(self, normalized_message: NormalizedMessage, keywords: List[str]) -> bool:
        """Filter a single normalized message based on keywords.

        Args:
            normalized_message: NormalizedMessage object to filter
            keywords: List of keywords to match against

        Returns:
            bool: True if filtering was successful, False otherwise
        """
        try:
            logger.info(f"Filtering normalized message {normalized_message.id}")
            
            # Check if any keyword matches
            text = normalized_message.normalized_text.lower()
            matches = any(keyword.lower() in text for keyword in keywords)
            
            if matches:
                # Create filtered message record
                filtered_msg = FilteredMessage(
                    original_message_id=normalized_message.original_message_id,
                    normalized_text=normalized_message.normalized_text
                )
                
                # Save changes
                self.db.add(filtered_msg)
                self.db.commit()
                
                logger.info(f"Successfully filtered message {normalized_message.id}")
                return True
            
            logger.info(f"Message {normalized_message.id} did not match keywords")
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error filtering message {normalized_message.id}: {e}")
            return False

    def filter_messages(self, keywords: List[str], batch_size: int = 100) -> int:
        """Filter all normalized messages in batches based on keywords.

        Args:
            keywords: List of keywords to match against
            batch_size: Number of messages to process in each batch

        Returns:
            Number of successfully filtered messages
        """
        logger.info(f"Starting batch filtering with keywords: {keywords}")
        filtered_count = 0
        offset = 0
        batch_number = 0
        
        while True:
            batch_number += 1
            logger.info(f"Processing batch {batch_number} (offset: {offset})")
            
            # Get batch of normalized messages
            messages = self.db.query(NormalizedMessage)\
                .offset(offset)\
                .limit(batch_size)\
                .all()
            
            if not messages:
                logger.info("No more messages to filter")
                break
                
            logger.info(f"Found {len(messages)} messages in batch {batch_number}")
            
            # Process batch
            batch_success = 0
            for message in messages:
                if self.filter_message(message, keywords):
                    filtered_count += 1
                    batch_success += 1
            
            logger.info(f"Batch {batch_number} completed. Matches: {batch_success}/{len(messages)}")
            offset += batch_size
        
        logger.info(f"Filtering completed. Total filtered: {filtered_count}")
        return filtered_count