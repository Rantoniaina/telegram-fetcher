"""Tests for the cleanup service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.cleanup import CleanupService
from src.models import Message, NormalizedMessage

@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    session = Mock()
    return session

@pytest.fixture
def cleanup_service(mock_db):
    """CleanupService fixture."""
    return CleanupService(mock_db)

def test_cleanup_database_all(cleanup_service, mock_db):
    """Test database cleanup for all messages."""
    # Setup
    mock_db.query.return_value.delete.return_value = None
    mock_db.commit.return_value = None
    
    # Execute
    result = cleanup_service.cleanup_database()
    
    # Verify
    assert result is True
    assert mock_db.query.call_count == 2
    mock_db.query.assert_any_call(NormalizedMessage)
    mock_db.query.assert_any_call(Message)
    assert mock_db.query.return_value.delete.call_count == 2
    mock_db.commit.assert_called_once()

def test_cleanup_database_normalized_only(cleanup_service, mock_db):
    """Test database cleanup for normalized messages only."""
    # Setup
    mock_db.query.return_value.delete.return_value = None
    mock_db.commit.return_value = None
    
    # Execute
    result = cleanup_service.cleanup_database(message_type='normalized')
    
    # Verify
    assert result is True
    mock_db.query.assert_called_once_with(NormalizedMessage)
    mock_db.query.return_value.delete.assert_called_once()
    mock_db.commit.assert_called_once()

def test_cleanup_database_error(cleanup_service, mock_db):
    """Test database cleanup error handling."""
    # Setup
    mock_db.query.side_effect = Exception("Test error")
    
    # Execute
    result = cleanup_service.cleanup_database()
    
    # Verify
    assert result is False
    mock_db.rollback.assert_called_once()

def test_cleanup_media(cleanup_service):
    """Test media cleanup."""
    # Setup mock files
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'glob') as mock_glob, \
         patch.object(Path, 'unlink') as mock_unlink:
        mock_glob.return_value = [Path('test1.jpg'), Path('test2.jpg')]
        
        # Execute
        result = cleanup_service.cleanup_media()
        
        # Verify
        assert result is True
        assert mock_unlink.call_count == 2

def test_cleanup_media_no_directory(cleanup_service):
    """Test media cleanup when directory doesn't exist."""
    # Setup
    with patch.object(Path, 'exists', return_value=False):
        # Execute
        result = cleanup_service.cleanup_media()
        
        # Verify
        assert result is True

def test_cleanup_media_error(cleanup_service):
    """Test media cleanup error handling."""
    # Setup
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'glob', side_effect=Exception("Test error")):
        # Execute
        result = cleanup_service.cleanup_media()
        
        # Verify
        assert result is False

def test_cleanup_all_success(cleanup_service):
    """Test successful cleanup of both database and media."""
    with patch.object(cleanup_service, 'cleanup_database', return_value=True), \
         patch.object(cleanup_service, 'cleanup_media', return_value=True):
        # Execute
        result = cleanup_service.cleanup_all()
        
        # Verify
        assert result is True
        cleanup_service.cleanup_database.assert_called_once_with(None)
        cleanup_service.cleanup_media.assert_called_once()

def test_cleanup_database_only(cleanup_service):
    """Test cleanup with database_only flag."""
    with patch.object(cleanup_service, 'cleanup_database', return_value=True), \
         patch.object(cleanup_service, 'cleanup_media', return_value=True):
        # Execute
        result = cleanup_service.cleanup_all(database_only=True)
        
        # Verify
        assert result is True
        cleanup_service.cleanup_database.assert_called_once_with(None)
        cleanup_service.cleanup_media.assert_not_called()

def test_cleanup_media_only(cleanup_service):
    """Test cleanup with media_only flag."""
    with patch.object(cleanup_service, 'cleanup_database', return_value=True), \
         patch.object(cleanup_service, 'cleanup_media', return_value=True):
        # Execute
        result = cleanup_service.cleanup_all(media_only=True)
        
        # Verify
        assert result is True
        cleanup_service.cleanup_database.assert_not_called()
        cleanup_service.cleanup_media.assert_called_once()

def test_cleanup_database_with_message_type(cleanup_service):
    """Test cleanup with specific message type."""
    with patch.object(cleanup_service, 'cleanup_database', return_value=True), \
         patch.object(cleanup_service, 'cleanup_media', return_value=True):
        # Execute
        result = cleanup_service.cleanup_all(database_only=True, message_type='normalized')
        
        # Verify
        assert result is True
        cleanup_service.cleanup_database.assert_called_once_with('normalized')
        cleanup_service.cleanup_media.assert_not_called()

def test_cleanup_all_partial_failure(cleanup_service):
    """Test cleanup when one operation fails."""
    with patch.object(cleanup_service, 'cleanup_database', return_value=True), \
         patch.object(cleanup_service, 'cleanup_media', return_value=False):
        # Execute
        result = cleanup_service.cleanup_all()
        
        # Verify
        assert result is False

def test_cleanup_database_invalid_message_type(cleanup_service, mock_db):
    """Test cleanup with invalid message type."""
    # Execute
    result = cleanup_service.cleanup_database(message_type='invalid_type')
    
    # Verify
    assert result is True
    mock_db.query.assert_any_call(NormalizedMessage)
    mock_db.query.assert_any_call(Message)
    assert mock_db.query.return_value.delete.call_count == 2
    mock_db.commit.assert_called_once()

def test_cleanup_database_transaction_error(cleanup_service, mock_db):
    """Test database cleanup with transaction error."""
    # Setup
    mock_db.commit.side_effect = Exception("Transaction error")
    
    # Execute
    result = cleanup_service.cleanup_database()
    
    # Verify
    assert result is False
    mock_db.rollback.assert_called_once()

def test_cleanup_media_permission_error(cleanup_service):
    """Test media cleanup with permission error."""
    # Setup
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'glob') as mock_glob, \
         patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
        mock_glob.return_value = [Path('test1.jpg')]
        
        # Execute
        result = cleanup_service.cleanup_media()
        
        # Verify
        assert result is False

def test_cleanup_database_invalid_message_type(cleanup_service, mock_db):
    """Test cleanup with invalid message type."""
    # Execute
    result = cleanup_service.cleanup_database(message_type='invalid_type')
    
    # Verify
    assert result is True
    mock_db.query.assert_any_call(NormalizedMessage)
    mock_db.query.assert_any_call(Message)
    assert mock_db.query.return_value.delete.call_count == 2
    mock_db.commit.assert_called_once()

def test_cleanup_database_transaction_error(cleanup_service, mock_db):
    """Test database cleanup with transaction error."""
    # Setup
    mock_db.commit.side_effect = Exception("Transaction error")
    
    # Execute
    result = cleanup_service.cleanup_database()
    
    # Verify
    assert result is False
    mock_db.rollback.assert_called_once()

def test_cleanup_media_permission_error(cleanup_service):
    """Test media cleanup with permission error."""
    # Setup
    with patch.object(Path, 'exists', return_value=True), \
         patch.object(Path, 'glob') as mock_glob, \
         patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
        mock_glob.return_value = [Path('test1.jpg')]
        
        # Execute
        result = cleanup_service.cleanup_media()
        
        # Verify
        assert result is False