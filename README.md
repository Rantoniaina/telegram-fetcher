# 📱 Telegram Message Fetcher

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-API-blue?style=for-the-badge&logo=telegram)](https://core.telegram.org/api)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

A powerful Python application for fetching and storing messages from Telegram channels. Built with modern best practices and a clean architecture. 🚀

## ✨ Features

- 📥 Fetch messages from Telegram channels
- 🔍 Filter messages by keywords
- 🖼️ Download and store media files
- 💾 Store messages in SQLite database
- 🖥️ CLI interface with rich formatting
- ⚡ Async support for better performance
- 📝 Comprehensive logging
- 🎯 Type hints and documentation
- 🛡️ Smart rate limit and ban handling

## 🛠️ Prerequisites

- 🐍 Python 3.8 or higher
- 🔑 Telegram API credentials (API ID and Hash)
- 🔐 Access to the target Telegram channel

## 🚀 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/telegram-fetcher.git
cd telegram-fetcher
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` with your Telegram API credentials and other settings.

## 🎮 Usage

The application provides a CLI interface with the following commands:

### 🚀 Initialize Project

To set up the project for first use:

```bash
python -m src.cli init
```

This command will:

- Create necessary directories
- Initialize the database
- Start required Docker services

### 📥 Fetch Messages

To fetch messages from the configured channel:

```bash
python -m src.cli fetch
```

Options:

- `--limit INTEGER`: Limit the number of messages to fetch
- `--no-media`: Skip downloading media files
- `--keywords LIST`: Filter messages by keywords (comma-separated)
- `--date STRING`: Filter messages by date (format: dd-MM-yyyy)
  > ⚠️ Note: Currently, the date filter fetches all messages first and then filters them locally. This means the initial fetch may take longer than expected as it doesn't utilize Telegram's API date filtering.
- `--verbose`: Enable verbose logging

### 📋 List Messages

To list stored messages:

```bash
python -m src.cli list
```

Options:

- `--limit INTEGER`: Number of messages to display (default: 100)
- `--skip INTEGER`: Number of messages to skip (default: 0)

### 🔄 Normalize Messages

To normalize stored messages:

```bash
python -m src.cli normalize
```

Options:

- `--limit INTEGER`: Maximum number of messages to normalize in each batch
- `--skip-empty`: Skip messages with empty text content
- `--verbose`: Show detailed progress for each message

### 🧹 Cleanup

To clean up stored messages and media files:

```bash
python -m src.cli cleanup
```

Options:

- `--force`, `-f`: Skip confirmation prompt before cleanup
- `--database-only`: Clean up only the database records
  - `--message-type`: Type of messages to clean ('messages' or 'normalized')
    - 'messages': Clean up raw message records
    - 'normalized': Clean up only normalized message records
- `--media-only`: Clean up only the downloaded media files

Examples:

```bash
# Clean everything with confirmation
python -m src.cli cleanup

# Clean everything without confirmation
python -m src.cli cleanup --force

# Clean only normalized messages
python -m src.cli cleanup --database-only --message-type normalized

# Clean only media files
python -m src.cli cleanup --media-only
```

### 🛑 Stop Services

To stop running Docker services:

```bash
python -m src.cli stop
```

Options:

- `--clear-database`: Clear database before stopping
- `--clear-media`: Clear media files before stopping

## 🛡️ Rate Limits and Error Handling

The application implements robust error handling for various Telegram API restrictions:

### Rate Limits

- Automatically handles Telegram's FloodWaitError
- Smart retry mechanism with exponential backoff
- Continues operation after waiting the required time

### Media Downloads

- Graceful handling of media download failures
- Automatic retries for temporary errors
- Skips problematic media files to continue operation

### Best Practices

- Respects Telegram API's rate limiting
- Implements safe error recovery
- Prevents account bans through smart throttling

## 📁 Project Structure

```
telegram-fetcher/
├── 📂 src/
│   ├── __init__.py
│   ├── cli.py           # CLI interface
│   ├── config.py        # Configuration management
│   ├── models.py        # Database models
│   ├── service.py       # Business logic
│   └── telegram_client.py # Telegram client wrapper
├── 📂 data/
│   ├── media/          # Downloaded media files
│   └── telegram.db     # SQLite database
├── 📂 tests/           # Test suite
├── 📄 requirements.txt # Dependencies
└── 📄 README.md       # This file
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
