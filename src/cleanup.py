from loguru import logger
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

from .config import settings
from .models import Message, NormalizedMessage


class CleanupService:
    def __init__(self, db: Session):
        self.db = db
        self.media_path = settings.MEDIA_PATH

    def cleanup_database(self, message_type=None):
        """Clear records from the database.
        
        Args:
            message_type (str, optional): Type of messages to clean ('messages' or 'normalized').
                                         If None or 'messages', cleans all records.
        """
        try:
            if message_type == 'normalized':
                self.db.query(NormalizedMessage).delete()
            else:
                # For 'messages' type or no parameter, delete both tables to maintain referential integrity
                self.db.query(NormalizedMessage).delete()
                self.db.query(Message).delete()
            
            self.db.commit()
            logger.info(f"Successfully cleared {message_type or 'all'} messages from database")
            return True
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            self.db.rollback()
            return False

    def cleanup_media(self):
        """Delete all media files from the media directory."""
        try:
            if not self.media_path.exists():
                logger.warning(f"Media directory {self.media_path} does not exist")
                return True

            # Delete all files in media directory
            files = list(self.media_path.glob("*"))
            file_count = 0
            for file_path in files:
                file_path.unlink()
                file_count += 1

            logger.info(f"Successfully deleted {file_count} media files")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up media files: {e}")
            return False

    def cleanup_all(self, database_only=False, media_only=False, message_type=None):
        """Clean up database records and/or media files.
        
        Args:
            database_only (bool): Only clean the database
            media_only (bool): Only clean the media files
            message_type (str, optional): Type of messages to clean when database_only is True
        """
        db_success = True
        media_success = True
        
        if not media_only:
            db_success = self.cleanup_database(message_type)
        
        if not database_only:
            media_success = self.cleanup_media()
            
        return db_success and media_success