"""Tests for the message service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, call
from datetime import datetime
from src.service import MessageService
from src.models import Message

class AsyncIterator:
    """Helper class to mock async iterators."""
    def __init__(self, items):
        self.items = items.copy()  # Make a copy to avoid modifying original

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return self.items.pop(0)
        except IndexError:
            raise StopAsyncIteration

class MockTelegramMessage:
    """Mock Telegram message for testing."""
    def __init__(self, id, text, chat_id=123, sender_id=456, media=None):
        self.id = id
        self.text = text
        self.date = datetime.now()
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.media = media
        self.chat = Mock(participants_count=10)

@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    db = Mock()
    db.query.return_value = db
    db.filter.return_value = db
    db.offset.return_value = db
    db.limit.return_value = db
    return db

@pytest.fixture
def service(mock_db):
    """MessageService fixture with mocked database."""
    return MessageService(mock_db)

def test_get_messages(service, mock_db):
    """Test retrieving messages from database."""
    # Setup mock data
    expected_messages = [
        Message(message_id=1, text="Test 1", date=datetime.now()),
        Message(message_id=2, text="Test 2", date=datetime.now())
    ]
    mock_db.all.return_value = expected_messages
    
    # Test with default parameters
    messages = service.get_messages()
    assert messages == expected_messages
    
    # Verify query building
    mock_db.query.assert_called_once_with(Message)
    mock_db.offset.assert_called_once_with(0)
    mock_db.limit.assert_called_once_with(100)

def test_get_messages_with_pagination(service, mock_db):
    """Test retrieving messages with custom pagination."""
    # Setup mock data
    expected_messages = [Message(message_id=3, text="Test 3", date=datetime.now())]
    mock_db.all.return_value = expected_messages
    
    # Test with custom parameters
    messages = service.get_messages(skip=10, limit=1)
    assert messages == expected_messages
    
    # Verify query building
    mock_db.query.assert_called_once_with(Message)
    mock_db.offset.assert_called_once_with(10)
    mock_db.limit.assert_called_once_with(1)

def test_get_message_by_id(service, mock_db):
    """Test retrieving a specific message by ID."""
    # Setup mock data
    expected_message = Message(message_id=1, text="Test", date=datetime.now())
    mock_db.first.return_value = expected_message
    
    # Test getting specific message
    message = service.get_message(1)
    assert message == expected_message
    
    # Verify query building
    mock_db.query.assert_called_once_with(Message)
    mock_db.filter.assert_called_once()

@pytest.mark.asyncio
async def test_process_messages(service, mock_db):
    """Test processing messages from Telegram."""
    # Setup mock messages
    mock_messages = [
        MockTelegramMessage(id=1, text="Test 1"),
        MockTelegramMessage(id=2, text="Test 2"),
        MockTelegramMessage(id=3, text="Test 3")
    ]
    
    # Setup mock fetcher
    mock_fetcher = AsyncMock()
    mock_fetcher.__aenter__.return_value = mock_fetcher
    mock_fetcher.fetch_messages = Mock(return_value=AsyncIterator(mock_messages))
    
    # Setup progress callback
    mock_progress = Mock()
    
    with patch('src.service.TelegramFetcher', return_value=mock_fetcher):
        # Process messages
        await service.process_messages(
            limit=5,
            download_media=True,
            progress_callback=mock_progress
        )
    
    # Verify database operations
    assert mock_db.merge.call_count == len(mock_messages)
    assert mock_db.commit.call_count == len(mock_messages)
    assert mock_progress.call_count == len(mock_messages)

@pytest.mark.asyncio
async def test_process_messages_with_media(service, mock_db):
    """Test processing messages with media attachments."""
    # Setup mock message with media
    mock_message = MockTelegramMessage(
        id=1,
        text="Test with media",
        media=Mock()  # Add media mock
    )
    
    # Setup mock fetcher
    mock_fetcher = AsyncMock()
    mock_fetcher.__aenter__.return_value = mock_fetcher
    mock_fetcher.fetch_messages = Mock(return_value=AsyncIterator([mock_message]))
    mock_fetcher.download_media = AsyncMock(return_value="media/test.jpg")
    
    with patch('src.service.TelegramFetcher', return_value=mock_fetcher):
        # Process message with media
        await service.process_messages(download_media=True)
    
    # Verify media download and database operations
    mock_fetcher.download_media.assert_called_once_with(mock_message)
    mock_db.merge.assert_called_once()
    assert mock_db.merge.call_args[0][0].media_path == "media/test.jpg"

@pytest.mark.asyncio
async def test_process_messages_error_handling(service, mock_db):
    """Test error handling during message processing."""
    # Setup mock message that will cause an error
    mock_message = MockTelegramMessage(id=1, text="Test error")
    mock_db.merge.side_effect = Exception("Database error")
    
    # Setup mock fetcher
    mock_fetcher = AsyncMock()
    mock_fetcher.__aenter__.return_value = mock_fetcher
    mock_fetcher.fetch_messages = Mock(return_value=AsyncIterator([mock_message]))
    
    with patch('src.service.TelegramFetcher', return_value=mock_fetcher):
        # Process messages with error
        await service.process_messages()
    
    # Verify error handling
    mock_db.rollback.assert_called_once()

def test_get_unnormalized_messages(service, mock_db):
    """Test retrieving unnormalized messages without pagination."""
    # Setup mock data
    expected_messages = [
        Message(message_id=1, text="Test 1", date=datetime.now(), is_normalized=False),
        Message(message_id=2, text="Test 2", date=datetime.now(), is_normalized=False)
    ]
    mock_db.all.return_value = expected_messages
    
    # Test with default parameters
    messages = service.get_unnormalized_messages()
    assert messages == expected_messages
    
    # Verify query building
    mock_db.query.assert_called_once_with(Message)
    mock_db.filter.assert_called_once()
    mock_db.all.assert_called_once()

def test_get_unnormalized_messages_with_pagination(service, mock_db):
    """Test retrieving unnormalized messages with pagination."""
    # Setup mock data
    expected_messages = [Message(message_id=3, text="Test 3", date=datetime.now(), is_normalized=False)]
    mock_db.all.return_value = expected_messages
    
    # Test with pagination parameters
    messages = service.get_unnormalized_messages(skip=10, limit=1)
    assert messages == expected_messages
    
    # Verify query building
    mock_db.query.assert_called_once_with(Message)
    mock_db.filter.assert_called_once()
    mock_db.offset.assert_called_once_with(10)
    mock_db.limit.assert_called_once_with(1)
    mock_db.all.assert_called_once()