"""Tests for the Telegram client wrapper."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from pathlib import Path
from src.telegram_client import TelegramFetcher
from unittest.mock import call
from telethon.errors import FloodWaitError

@pytest.fixture
def mock_telethon_client():
    """Mock Telethon client fixture."""
    client = AsyncMock()
    client.start.return_value = True
    client.disconnect.return_value = True
    return client

@pytest.fixture
def mock_settings():
    """Mock settings fixture."""
    settings = Mock(
        TELEGRAM_API_ID="123",
        TELEGRAM_API_HASH="abc",
        TELEGRAM_PHONE="+1234567890",
        TELEGRAM_CHANNEL="test_channel",
        MEDIA_PATH=Path("media"),
        SESSION_NAME="test_session",
        API_ID="123",
        API_HASH="abc",
        CHANNEL_NAME="test_channel"
    )
    return settings

@pytest.fixture
def telegram_client(mock_telethon_client, mock_settings):
    """Telegram client wrapper fixture."""
    with patch('src.telegram_client.settings', mock_settings), \
         patch('src.telegram_client.TelegramClient', return_value=mock_telethon_client):
        client = TelegramFetcher()
        return client

@pytest.fixture
def sample_messages():
    """Sample messages fixture."""
    return [
        Mock(
            id=1,
            text="Test message 1",
            date=datetime.now(),
            media=None
        ),
        Mock(
            id=2,
            text="Test message 2",
            date=datetime.now(),
            media=Mock()
        )
    ]

@pytest.mark.asyncio
async def test_connect(telegram_client, mock_telethon_client):
    """Test connecting to Telegram."""
    async with telegram_client:
        pass
    
    # Verify
    mock_telethon_client.start.assert_called_once()
    mock_telethon_client.disconnect.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_messages(telegram_client, mock_telethon_client, sample_messages):
    """Test fetching messages from a channel."""
    # Setup mock channel and messages
    mock_channel = Mock()
    mock_channel.title = "Test Channel"
    mock_telethon_client.get_entity = AsyncMock(return_value=mock_channel)
    mock_telethon_client.get_messages = AsyncMock(side_effect=[
        Mock(total=len(sample_messages)),  # First call returns total
        sample_messages  # Second call returns actual messages
    ])
    
    # Fetch messages
    messages = []
    async with telegram_client:
        async for msg in telegram_client.fetch_messages(limit=10):
            messages.append(msg)
    
    # Verify
    assert len(messages) == len(sample_messages)
    mock_telethon_client.get_entity.assert_called_once()
    assert mock_telethon_client.get_messages.call_count == 2

@pytest.mark.asyncio
async def test_download_media(telegram_client, mock_telethon_client):
    """Test downloading media from a message."""
    # Setup mock
    mock_message = AsyncMock()
    mock_message.media = Mock()
    mock_message.id = 123
    mock_message.download_media = AsyncMock(return_value="downloaded_file.jpg")
    
    # Download media
    async with telegram_client:
        result = await telegram_client.download_media(mock_message)
    
    # Verify
    assert result is not None
    mock_message.download_media.assert_called_once()

@pytest.mark.asyncio
async def test_download_media_with_rate_limit(telegram_client, mock_telethon_client):
    """Test handling rate limits during media download."""
    # Setup mock
    mock_message = AsyncMock()
    mock_message.media = Mock()
    mock_message.id = 123
    
    # Simulate rate limit on first attempt, then success
    flood_error = FloodWaitError(2)  # 2 seconds wait
    mock_message.download_media = AsyncMock(side_effect=[flood_error, "downloaded_file.jpg"])
    
    # Download media
    async with telegram_client:
        result = await telegram_client.download_media(mock_message)
    
    # Verify
    assert result is not None
    assert mock_message.download_media.call_count == 2

@pytest.mark.asyncio
async def test_download_media_error(telegram_client, mock_telethon_client):
    """Test handling general errors during media download."""
    # Setup mock
    mock_message = AsyncMock()
    mock_message.media = Mock()
    mock_message.id = 123
    mock_message.download_media = AsyncMock(side_effect=Exception("Download failed"))
    
    # Download media
    async with telegram_client:
        result = await telegram_client.download_media(mock_message)
    
    # Verify
    assert result is None
    mock_message.download_media.assert_called_once()

@pytest.mark.asyncio
async def test_download_media_no_media(telegram_client, mock_telethon_client):
    """Test attempting to download from message without media."""
    # Setup mock
    mock_message = AsyncMock()
    mock_message.media = None
    mock_message.id = 123
    
    # Download media
    async with telegram_client:
        result = await telegram_client.download_media(mock_message)
    
    # Verify
    assert result is None
    assert not mock_message.download_media.called

@pytest.mark.asyncio
async def test_fetch_messages_with_limit(telegram_client, mock_telethon_client):
    """Test fetching messages with a specific limit."""
    # Setup mock
    mock_channel = Mock()
    mock_channel.title = "Test Channel"
    mock_telethon_client.get_entity = AsyncMock(return_value=mock_channel)
    
    # Create mock messages
    mock_messages = [Mock(id=i, text=f"Test message {i}") for i in range(5)]
    limited_messages = mock_messages[:3]  # Only return 3 messages when limit is 3
    
    mock_telethon_client.get_messages = AsyncMock(side_effect=[
        Mock(total=len(mock_messages)),  # First call returns total
        limited_messages  # Second call returns limited messages
    ])
    
    # Fetch messages with limit
    messages = []
    async with telegram_client:
        async for msg in telegram_client.fetch_messages(limit=3):
            messages.append(msg)
    
    # Verify
    assert len(messages) == 3  # Should respect the limit
    mock_telethon_client.get_entity.assert_called_once()
    assert mock_telethon_client.get_messages.call_count == 2
    # Verify the second call to get_messages had the correct limit
    mock_telethon_client.get_messages.assert_has_calls([
        call(mock_channel, limit=0),  # First call to get total
        call(mock_channel, limit=3)   # Second call with our limit
    ])