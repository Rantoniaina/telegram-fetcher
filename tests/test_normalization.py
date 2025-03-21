"""Tests for the normalization service."""

import pytest
from unittest.mock import Mock
from src.normalization import NormalizationService
from src.models import Message, NormalizedMessage

@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    session = Mock()
    return session

@pytest.fixture
def normalization_service(mock_db):
    """NormalizationService fixture."""
    return NormalizationService(mock_db)

def test_clean_message(normalization_service):
    """Test message text cleaning functionality."""
    # Test normal text cleaning
    text = "Hello World! http://example.com #hashtag"
    result = normalization_service.clean_message(text)
    assert result == "hello world"

    # Test empty text
    assert normalization_service.clean_message("") == ""
    
    # Test None value
    assert normalization_service.clean_message(None) == ""

def test_normalize_message_with_text(normalization_service, mock_db):
    """Test message normalization with valid text."""
    message = Message(id=1, text="Hello World!")
    
    result = normalization_service.normalize_message(message)
    
    assert result is True
    assert message.is_normalized is True
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_normalize_message_empty_text(normalization_service, mock_db):
    """Test message normalization with empty text."""
    message = Message(id=1, text="")
    
    result = normalization_service.normalize_message(message)
    
    assert result is True
    assert message.is_normalized is True
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()

def test_normalize_messages_batch(normalization_service, mock_db):
    """Test batch message normalization."""
    messages = [
        Message(id=1, text="Hello", is_normalized=False),
        Message(id=2, text="World", is_normalized=False),
        Message(id=3, text="", is_normalized=False)
    ]
    mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = messages
    mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.side_effect = [messages, []]
    
    result = normalization_service.normalize_messages(batch_size=2)
    
    assert result == 2  # Only 2 messages should be normalized (empty one is skipped)
    assert all(msg.is_normalized for msg in messages)

def test_normalize_messages_with_skip_empty(normalization_service, mock_db):
    """Test batch normalization with skip_empty option."""
    messages = [
        Message(id=1, text="", is_normalized=False),
        Message(id=2, text=" ", is_normalized=False),
        Message(id=3, text="Hello", is_normalized=False)
    ]
    mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = messages
    mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.side_effect = [messages, []]
    
    result = normalization_service.normalize_messages(batch_size=3, skip_empty=True)
    
    assert result == 1  # Only one message should be normalized
    assert all(msg.is_normalized for msg in messages)
    # Verify empty messages were marked as normalized without creating NormalizedMessage
    assert mock_db.add.call_count == 1