"""Tests for the cleanup service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.cleanup import CleanupService
from src.models import Message

@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    session = Mock()
    return session

@pytest.fixture
def cleanup_service(mock_db):
    """CleanupService fixture."""
    return CleanupService(mock_db)

def test_cleanup_database(cleanup_service, mock_db):
    """Test database cleanup."""
    # Setup
    mock_db.query.return_value.delete.return_value = None
    mock_db.commit.return_value = None
    
    # Execute
    result = cleanup_service.cleanup_database()
    
    # Verify
    assert result is True
    mock_db.query.assert_called_once_with(Message)
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
        cleanup_service.cleanup_database.assert_called_once()
        cleanup_service.cleanup_media.assert_called_once()

def test_cleanup_all_partial_failure(cleanup_service):
    """Test cleanup when one operation fails."""
    with patch.object(cleanup_service, 'cleanup_database', return_value=True), \
         patch.object(cleanup_service, 'cleanup_media', return_value=False):
        # Execute
        result = cleanup_service.cleanup_all()
        
        # Verify
        assert result is False