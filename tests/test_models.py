"""Tests for database models."""

from datetime import datetime
import pytest
from src.models import Message

def test_message_creation():
    """Test creating a new message object."""
    message = Message(
        message_id=1,
        text="Test message",
        date=datetime.now(),
        chat_id=123456,
        sender_id=789012
    )
    assert message.message_id == 1
    assert message.text == "Test message"
    assert message.chat_id == 123456
    assert message.sender_id == 789012
    assert isinstance(message.media_files, list)
    assert len(message.media_files) == 0

def test_message_with_media():
    """Test creating a message with media."""
    from src.models import MediaFile
    message = Message(
        message_id=1,
        text="Test message with media",
        date=datetime.now(),
        chat_id=123456,
        sender_id=789012
    )
    media = MediaFile(
        file_path="media/photo.jpg",
        file_type="photo"
    )
    message.media_files.append(media)
    assert len(message.media_files) == 1
    assert message.media_files[0].file_path == "media/photo.jpg"

def test_message_str_representation():
    """Test string representation of a message."""
    message = Message(
        id=1,
        message_id=123,
        text="Test message",
        date=datetime.now(),
        chat_id=123456,
        sender_id=789012
    )
    expected = f"<Message(id=1, message_id=123)>"
    assert str(message) == expected

def test_message_equality():
    """Test message equality comparison."""
    date = datetime.now()
    msg1 = Message(message_id=1, text="Test", date=date, chat_id=123, sender_id=456)
    msg2 = Message(message_id=1, text="Test", date=date, chat_id=123, sender_id=456)
    msg3 = Message(message_id=2, text="Test", date=date, chat_id=123, sender_id=456)
    
    assert msg1.message_id == msg2.message_id
    assert msg1.message_id != msg3.message_id