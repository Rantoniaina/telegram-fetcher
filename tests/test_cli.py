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
    mock_db.commit.return_value = None  # Ensure commit doesn't raise exception
    
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
        keywords=None,  # no keywords by default
        date=None,  # date filter is None by default
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
            "--keywords", "important,update",
            "--no-media",
            "--verbose"
        ])
    
    assert result.exit_code == 0
    mock_service.process_messages.assert_called_once_with(
        limit=10,
        download_media=False,  # no_media is True
        keywords=["important", "update"],
        date=None,  # date filter is None by default
        progress_callback=ANY
    )

def test_fetch_command_with_date_filter(runner, mock_service, mock_db):
    """Test fetch command with date filter."""
    async def mock_process_messages(*args, **kwargs):
        return None

    mock_service.process_messages.side_effect = mock_process_messages
    test_date = "01-01-2024"

    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.MessageService', return_value=mock_service), \
         patch('src.cli.init_db'), \
         patch('src.cli.Progress'):
        result = runner.invoke(app, ["fetch", "--date", test_date])
    
    assert result.exit_code == 0
    mock_service.process_messages.assert_called_once_with(
        limit=None,
        download_media=True,
        keywords=None,
        date=test_date,
        progress_callback=ANY
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

@pytest.fixture
def mock_cleanup_service():
    """Mock CleanupService fixture."""
    service = Mock()
    service.cleanup_all = Mock(return_value=True)
    return service

def test_cleanup_command_basic(runner, mock_db, mock_cleanup_service):
    """Test the basic cleanup command."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.CleanupService', return_value=mock_cleanup_service), \
         patch('src.cli.Confirm.ask', return_value=True):
        result = runner.invoke(app, ["cleanup"])
    
    assert result.exit_code == 0
    mock_cleanup_service.cleanup_all.assert_called_once_with(
        database_only=False,
        media_only=False,
        message_type=None
    )

def test_cleanup_command_force(runner, mock_db, mock_cleanup_service):
    """Test cleanup command with force option."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.CleanupService', return_value=mock_cleanup_service):
        result = runner.invoke(app, ["cleanup", "--force"])
    
    assert result.exit_code == 0
    mock_cleanup_service.cleanup_all.assert_called_once()

def test_cleanup_command_database_only(runner, mock_db, mock_cleanup_service):
    """Test cleanup command with database-only option."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.CleanupService', return_value=mock_cleanup_service), \
         patch('src.cli.Confirm.ask', return_value=True):
        result = runner.invoke(app, ["cleanup", "--database-only", "--message-type", "normalized"])
    
    assert result.exit_code == 0
    mock_cleanup_service.cleanup_all.assert_called_once_with(
        database_only=True,
        media_only=False,
        message_type="normalized"
    )

def test_cleanup_command_invalid_options(runner, mock_db, mock_cleanup_service):
    """Test cleanup command with invalid options combination."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.CleanupService', return_value=mock_cleanup_service):
        result = runner.invoke(app, ["cleanup", "--database-only", "--media-only"])
    
    assert result.exit_code == 0
    assert "Cannot use both" in result.stdout
    mock_cleanup_service.cleanup_all.assert_not_called()

def test_cleanup_command_failure(runner, mock_db, mock_cleanup_service):
    """Test cleanup command when operation fails."""
    mock_cleanup_service.cleanup_all.return_value = False
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.CleanupService', return_value=mock_cleanup_service), \
         patch('src.cli.Confirm.ask', return_value=True):
        result = runner.invoke(app, ["cleanup"])
    
    assert result.exit_code == 1
    assert "errors occurred" in result.stdout

@pytest.fixture
def mock_normalization_service():
    """Mock NormalizationService fixture."""
    service = Mock()
    service.normalize_messages = Mock(return_value=5)
    return service

def test_stop_command_basic(runner):
    """Test basic stop command without cleanup."""
    with patch('subprocess.run') as mock_run:
        result = runner.invoke(app, ["stop"])
    
    assert result.exit_code == 0
    assert "stopped successfully" in result.stdout
    mock_run.assert_called_once_with(['docker-compose', 'down'], check=True)

def test_stop_command_with_cleanup(runner, mock_db):
    """Test stop command with data cleanup."""
    mock_cleanup_service = Mock()
    mock_cleanup_service.cleanup_all.return_value = True
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.CleanupService', return_value=mock_cleanup_service), \
         patch('subprocess.run') as mock_run:
        result = runner.invoke(app, ["stop", "--clear-database", "--clear-media"])
    
    assert result.exit_code == 0
    mock_cleanup_service.cleanup_all.assert_called_once()
    mock_run.assert_called_once_with(['docker-compose', 'down'], check=True)

def test_stop_command_docker_error(runner):
    """Test stop command when Docker operation fails."""
    with patch('subprocess.run', side_effect=FileNotFoundError("Docker not found")):
        result = runner.invoke(app, ["stop"])
    
    assert "Docker Compose not found" in result.stdout

def test_stop_command_cleanup_error(runner, mock_db):
    """Test stop command when cleanup fails."""
    mock_cleanup_service = Mock()
    mock_cleanup_service.cleanup_all.return_value = False
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.CleanupService', return_value=mock_cleanup_service), \
         patch('subprocess.run') as mock_run:
        result = runner.invoke(app, ["stop", "--clear-database"])
    
    assert result.exit_code == 1
    assert "errors occurred during cleanup" in result.stdout

def test_init_command_basic(runner):
    """Test basic initialization command."""
    with patch('src.cli.Path.exists', return_value=False), \
         patch('src.cli.Path.mkdir') as mock_mkdir, \
         patch('src.cli.init_db') as mock_init_db, \
         patch('subprocess.run') as mock_run:
        # Mock Docker Compose check (no containers running)
        mock_run.side_effect = [
            Mock(stdout='', returncode=0),  # docker-compose ps
            Mock(returncode=0)  # docker-compose up
        ]
        
        result = runner.invoke(app, ["init"])
    
    assert result.exit_code == 0
    mock_mkdir.assert_called_once()
    mock_init_db.assert_called_once()
    assert mock_run.call_count == 2
    assert "initialized successfully" in result.stdout

def test_init_command_docker_running(runner):
    """Test init command when Docker services are already running."""
    with patch('src.cli.Path.exists', return_value=True), \
         patch('src.cli.init_db'), \
         patch('subprocess.run') as mock_run:
        # Mock Docker Compose check (containers running)
        mock_run.return_value = Mock(stdout='container1\n', returncode=0)
        
        result = runner.invoke(app, ["init"])
    
    assert result.exit_code == 0
    assert "already running" in result.stdout

def test_init_command_docker_error(runner):
    """Test init command with Docker error."""
    with patch('src.cli.Path.exists', return_value=True), \
         patch('src.cli.init_db'), \
         patch('subprocess.run', side_effect=FileNotFoundError()):
        result = runner.invoke(app, ["init"])
    
    assert result.exit_code == 0  # Non-fatal error
    assert "Docker Compose not found" in result.stdout

def test_init_command_database_error(runner):
    """Test init command with database error."""
    with patch('src.cli.Path.exists', return_value=True), \
         patch('src.cli.init_db', side_effect=Exception("Database error")), \
         patch('subprocess.run'):
        result = runner.invoke(app, ["init"])
    
    assert result.exit_code == 1
    assert "Error during initialization" in result.stdout

def test_normalize_command_basic(runner, mock_db, mock_normalization_service):
    """Test the basic normalize command."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.NormalizationService', return_value=mock_normalization_service), \
         patch('src.cli.Progress'):
        result = runner.invoke(app, ["normalize"])
    
    assert result.exit_code == 0
    mock_normalization_service.normalize_messages.assert_called_once_with(batch_size=100)
    assert "5 messages normalized" in result.stdout

def test_normalize_command_with_options(runner, mock_db, mock_normalization_service):
    """Test normalize command with options."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.NormalizationService', return_value=mock_normalization_service), \
         patch('src.cli.Progress'):
        result = runner.invoke(app, ["normalize", "--limit", "50", "--skip-empty", "--verbose"])
    
    assert result.exit_code == 0
    mock_normalization_service.normalize_messages.assert_called_once_with(batch_size=50)

def test_normalize_command_error(runner, mock_db):
    """Test normalize command error handling."""
    with patch('src.cli.get_db', return_value=iter([mock_db])), \
         patch('src.cli.NormalizationService', side_effect=Exception("Test error")), \
         patch('src.cli.Progress'):
        result = runner.invoke(app, ["normalize"])
    
    assert result.exit_code == 1
    assert "Error" in result.stdout