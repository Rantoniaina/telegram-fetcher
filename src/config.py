from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Telegram API credentials
    API_ID: int
    API_HASH: str
    CHANNEL_NAME: str
    
    # Database settings
    DATABASE_URL: str = "sqlite:///data/telegram.db"
    
    # Media storage
    MEDIA_PATH: Path = Path("data/media")
    
    # Session name for Telegram client
    SESSION_NAME: str = "telegram_fetcher"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 