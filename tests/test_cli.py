"""Tests for the CLI interface."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, ANY
from typer.testing import CliRunner
from datetime import datetime
from src.cli import app
from src.models import Message

def run_async(coro):
    """Helper function to run coroutines in tests."""
    import asyncio
    return asyncio.run(coro)

@pytest.fixture
def mock_service():
    """Mock MessageService fixture."""
    service = Mock()
    service.get_messages = Mock()
    service.get_message = Mock()
    service.process_messages = AsyncMock()
    service.process_messages.return_value = None  # Ensure it returns None when awaited
    return service

@pytest.fixture
def mock_db():
    """Mock database session fixture."""
    session = Mock()
    return session

@pytest.fixture
def runner():
    """Typer CLI runner fixture."""
    return CliRunner()

def test_list_command(runner, mock_service, mock_db):
    """Test the list command."""
    # Setup mock data
    messages = [
        Message(message_id=1, text="Test 1", date=datetime.now()),
        Message(message_id=2, text="Test 2", date=datetime.now())
    ]
    mock_service.get_messages.return_value = messages
    
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.MessageService', return_value=mock_service):
        result = runner.invoke(app, ["list"])
    
    assert result.exit_code == 0
    assert "Test 1" in result.stdout
    assert "Test 2" in result.stdout

def test_list_command_with_pagination(runner, mock_service, mock_db):
    """Test the list command with pagination."""
    # Setup mock data
    messages = [Message(message_id=3, text="Test 3", date=datetime.now())]
    mock_service.get_messages.return_value = messages
    
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.MessageService', return_value=mock_service):
        result = runner.invoke(app, ["list", "--skip", "2", "--limit", "1"])
    
    assert result.exit_code == 0
    assert "Test 3" in result.stdout
    mock_service.get_messages.assert_called_once_with(skip=2, limit=1)

def test_fetch_command(runner, mock_service, mock_db):
    """Test the fetch command."""
    async def mock_process_messages(*args, **kwargs):
        return None

    mock_service.process_messages.side_effect = mock_process_messages

    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.MessageService', return_value=mock_service), \
         patch('src.cli.init_db'), \
         patch('src.cli.Progress'):  # Mock the progress bar
        result = runner.invoke(app, ["fetch"])
    
    assert result.exit_code == 0
    mock_service.process_messages.assert_called_once_with(
        limit=None,
        download_media=True,  # no_media is False by default
        progress_callback=ANY  # Use ANY to match any callback function
    )

def test_fetch_command_with_options(runner, mock_service, mock_db):
    """Test the fetch command with options."""
    async def mock_process_messages(*args, **kwargs):
        return None

    mock_service.process_messages.side_effect = mock_process_messages

    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.MessageService', return_value=mock_service), \
         patch('src.cli.init_db'), \
         patch('src.cli.Progress'):  # Mock the progress bar
        result = runner.invoke(app, [
            "fetch",
            "--limit", "10",
            "--no-media"
        ])
    
    assert result.exit_code == 0
    mock_service.process_messages.assert_called_once_with(
        limit=10,
        download_media=False,
        progress_callback=ANY  # Use ANY to match any callback function
    )

def test_list_command_error_handling(runner, mock_db):
    """Test error handling in list command."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.MessageService', side_effect=Exception("Test error")):
        result = runner.invoke(app, ["list"])
    
    assert result.exit_code == 1
    assert "Error" in result.stdout

@pytest.mark.asyncio
async def test_fetch_command_error_handling(runner, mock_db):
    """Test error handling in fetch command."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.MessageService', side_effect=Exception("Test error")), \
         patch('src.cli.init_db'), \
         patch('src.cli.Progress'):  # Mock the progress bar
        result = runner.invoke(app, ["fetch"])
    
    assert result.exit_code == 1
    assert "Error" in result.stdout 