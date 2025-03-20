from loguru import logger
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

from .config import settings
from .models import Message


class CleanupService:
    def __init__(self, db: Session):
        self.db = db
        self.media_path = settings.MEDIA_PATH

    def cleanup_database(self):
        """Clear all records from the database."""
        try:
            # Delete all messages
            self.db.query(Message).delete()
            self.db.commit()
            logger.info("Successfully cleared all messages from database")
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

    def cleanup_all(self):
        """Clean up both database and media files."""
        db_success = self.cleanup_database()
        media_success = self.cleanup_media()
        return db_success and media_success