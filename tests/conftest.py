"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import Mock
from datetime import datetime
from src.config import Settings
from src.models import Message

@pytest.fixture
def settings():
    """Test settings fixture."""
    return Settings(
        API_ID=123456,
        API_HASH="test_hash",
        CHANNEL_NAME="test_channel",
        DATABASE_URL="sqlite:///test.db"
    )

@pytest.fixture
def sample_messages():
    """Sample Telegram messages for testing."""
    messages = []
    for i in range(5):
        msg = Mock()
        msg.id = i + 1
        msg.date = datetime.now()
        msg.message = f"Test message {i + 1}"
        msg.media = None if i % 2 == 0 else Mock()
        messages.append(msg)
    return messages

@pytest.fixture
def telegram_message():
    """Sample Message model instance."""
    return Message(
        message_id=1,
        text="Test message",
        date=datetime.now(),
        chat_id=123456,
        sender_id=789012
    ) 