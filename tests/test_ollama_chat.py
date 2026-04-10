import os
import pytest
from unittest.mock import Mock, patch
from src.ollama_chat import OllamaClient

@pytest.fixture
def mock_httpx_client():
    with patch('httpx.Client') as mock_client:
        yield mock_client.return_value

@pytest.fixture
def ollama_client(mock_httpx_client):
    return OllamaClient()

def test_init_with_default_url():
    client = OllamaClient()
    assert client.base_url == 'http://localhost:11434'

def test_init_with_custom_url():
    custom_url = 'http://custom:1234'
    client = OllamaClient(base_url=custom_url)
    assert client.base_url == custom_url

def test_init_with_env_url(monkeypatch):
    env_url = 'http://env:5678'
    monkeypatch.setenv('OLLAMA_BASE_URL', env_url)
    client = OllamaClient()
    assert client.base_url == env_url

def test_check_health_success(ollama_client, mock_httpx_client):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.get.return_value = mock_response
    
    assert ollama_client.check_health() is True
    mock_httpx_client.get.assert_called_once_with(f"{ollama_client.base_url}/api/version")

def test_check_health_failure(ollama_client, mock_httpx_client):
    mock_httpx_client.get.side_effect = Exception('Connection error')
    
    assert ollama_client.check_health() is False
    mock_httpx_client.get.assert_called_once_with(f"{ollama_client.base_url}/api/version")

def test_chat_success(ollama_client, mock_httpx_client):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"response": "Test response"}
    mock_httpx_client.post.return_value = mock_response
    
    response = ollama_client.chat("Hello", model="test-model")
    assert response == "Test response"
    mock_httpx_client.post.assert_called_once_with(
        f"{ollama_client.base_url}/api/generate",
        json={"model": "test-model", "prompt": "Hello", "stream": False}
    )

def test_chat_with_default_model(ollama_client, mock_httpx_client, monkeypatch):
    monkeypatch.setenv('OLLAMA_MODEL', 'default-model')
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"response": "Test response"}
    mock_httpx_client.post.return_value = mock_response
    
    response = ollama_client.chat("Hello")
    assert response == "Test response"
    mock_httpx_client.post.assert_called_once_with(
        f"{ollama_client.base_url}/api/generate",
        json={"model": "default-model", "prompt": "Hello", "stream": False}
    )

def test_chat_failure(ollama_client, mock_httpx_client):
    error_message = "API error"
    mock_httpx_client.post.side_effect = Exception(error_message)
    
    response = ollama_client.chat("Hello")
    assert response == f"Error: {error_message}"
    mock_httpx_client.post.assert_called_once()