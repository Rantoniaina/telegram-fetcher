"""Tests for the filter service."""

import pytest
from unittest.mock import Mock
from src.filter import FilterService
from src.models import NormalizedMessage, FilteredMessage

@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    session = Mock()
    return session

@pytest.fixture
def filter_service(mock_db):
    """FilterService fixture."""
    return FilterService(mock_db)

def test_filter_message_with_match(filter_service, mock_db):
    """Test message filtering with matching keyword."""
    message = NormalizedMessage(id=1, normalized_text="Hello World", original_message_id=1)
    keywords = ["hello", "test"]
    
    result = filter_service.filter_message(message, keywords)
    
    assert result is True
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_filter_message_no_match(filter_service, mock_db):
    """Test message filtering with no matching keyword."""
    message = NormalizedMessage(id=1, normalized_text="Hello World", original_message_id=1)
    keywords = ["test", "example"]
    
    result = filter_service.filter_message(message, keywords)
    
    assert result is False
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

def test_filter_message_error_handling(filter_service, mock_db):
    """Test error handling during message filtering."""
    message = NormalizedMessage(id=1, normalized_text="Hello World", original_message_id=1)
    keywords = ["hello"]
    mock_db.add.side_effect = Exception("Database error")
    
    result = filter_service.filter_message(message, keywords)
    
    assert result is False
    mock_db.rollback.assert_called_once()

def test_filter_messages_batch(filter_service, mock_db):
    """Test batch message filtering."""
    messages = [
        NormalizedMessage(id=1, normalized_text="Hello World", original_message_id=1),
        NormalizedMessage(id=2, normalized_text="Test Message", original_message_id=2),
        NormalizedMessage(id=3, normalized_text="Another Example", original_message_id=3)
    ]
    mock_db.query.return_value.offset.return_value.limit.return_value.all.side_effect = [messages, []]
    keywords = ["hello", "test"]
    
    result = filter_service.filter_messages(keywords, batch_size=2)
    
    assert result == 2  # Two messages should match keywords
    assert mock_db.add.call_count == 2
    assert mock_db.commit.call_count == 2

def test_filter_messages_empty_batch(filter_service, mock_db):
    """Test batch filtering with no messages."""
    mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    keywords = ["test"]
    
    result = filter_service.filter_messages(keywords, batch_size=100)
    
    assert result == 0
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()