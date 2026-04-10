"""Tests for the config module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.config import Settings


def test_settings_default_values():
    """Test that default values are set correctly when not provided in env."""
    with patch.dict(os.environ, {
        "API_ID": "123456",
        "API_HASH": "test_hash",
        "CHANNEL_NAME": "test_channel"
    }):
        settings = Settings()
        
        # Check required values are loaded
        assert settings.API_ID == 123456
        assert settings.API_HASH == "test_hash"
        assert settings.CHANNEL_NAME == "test_channel"
        
        # Check default values
        assert settings.DATABASE_URL == "sqlite:///data/telegram.db"
        assert settings.MEDIA_PATH == Path("data/media")
        assert settings.SESSION_NAME == "telegram_fetcher"
        assert settings.OLLAMA_BASE_URL == "http://localhost:11434"
        assert settings.OLLAMA_MODEL == "llava"
        assert settings.OLLAMA_MAX_TOKENS == 2048
        assert settings.OLLAMA_TEMPERATURE == 0.8


def test_settings_custom_values():
    """Test that custom values override defaults when provided in env."""
    with patch.dict(os.environ, {
        "API_ID": "123456",
        "API_HASH": "test_hash",
        "CHANNEL_NAME": "test_channel",
        "DATABASE_URL": "sqlite:///custom.db",
        "MEDIA_PATH": "custom/media",
        "SESSION_NAME": "custom_session",
        "OLLAMA_BASE_URL": "http://custom:11434",
        "OLLAMA_MODEL": "custom_model",
        "OLLAMA_MAX_TOKENS": "4096",
        "OLLAMA_TEMPERATURE": "0.5"
    }):
        settings = Settings()
        
        # Check all values are loaded from environment
        assert settings.API_ID == 123456
        assert settings.API_HASH == "test_hash"
        assert settings.CHANNEL_NAME == "test_channel"
        assert settings.DATABASE_URL == "sqlite:///custom.db"
        assert settings.MEDIA_PATH == Path("custom/media")
        assert settings.SESSION_NAME == "custom_session"
        assert settings.OLLAMA_BASE_URL == "http://custom:11434"
        assert settings.OLLAMA_MODEL == "custom_model"
        assert settings.OLLAMA_MAX_TOKENS == 4096
        assert settings.OLLAMA_TEMPERATURE == 0.5


def test_settings_path_conversion():
    """Test that string paths are converted to Path objects."""
    with patch.dict(os.environ, {
        "API_ID": "123456",
        "API_HASH": "test_hash",
        "CHANNEL_NAME": "test_channel",
        "MEDIA_PATH": "custom/path/to/media"
    }):
        settings = Settings()
        
        assert isinstance(settings.MEDIA_PATH, Path)
        assert settings.MEDIA_PATH == Path("custom/path/to/media")


def test_settings_direct_init():
    """Test direct initialization of Settings with parameters."""
    settings = Settings(
        API_ID=987654,
        API_HASH="direct_hash",
        CHANNEL_NAME="direct_channel",
        DATABASE_URL="sqlite:///direct.db",
        MEDIA_PATH=Path("direct/media"),
        OLLAMA_TEMPERATURE=0.3
    )
    
    assert settings.API_ID == 987654
    assert settings.API_HASH == "direct_hash"
    assert settings.CHANNEL_NAME == "direct_channel"
    assert settings.DATABASE_URL == "sqlite:///direct.db"
    assert settings.MEDIA_PATH == Path("direct/media")
    assert settings.OLLAMA_TEMPERATURE == 0.3
    
    # Other values should still be defaults
    assert settings.SESSION_NAME == "telegram_fetcher"
    assert settings.OLLAMA_BASE_URL == "http://localhost:11434"
    assert settings.OLLAMA_MODEL == "llava"
    assert settings.OLLAMA_MAX_TOKENS == 2048