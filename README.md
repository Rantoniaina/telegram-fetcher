# 📱 Telegram Message Fetcher

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-API-blue?style=for-the-badge&logo=telegram)](https://core.telegram.org/api)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

A powerful Python application for fetching and storing messages from Telegram channels. Built with modern best practices and a clean architecture. 🚀

## ✨ Features

- 📥 Fetch messages from Telegram channels
- 🖼️ Download and store media files
- 💾 Store messages in SQLite database
- 🖥️ CLI interface with rich formatting
- ⚡ Async support for better performance
- 📝 Comprehensive logging
- 🎯 Type hints and documentation

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

### 📥 Fetch Messages

To fetch messages from the configured channel:

```bash
python -m src.cli fetch
```

Options:

- `--limit INTEGER`: Limit the number of messages to fetch
- `--no-media`: Skip downloading media files
- `--verbose`: Enable verbose logging

### 📋 List Messages

To list stored messages:

```bash
python -m src.cli list
```

Options:

- `--limit INTEGER`: Number of messages to display (default: 100)
- `--skip INTEGER`: Number of messages to skip (default: 0)

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
├── requirements.txt
├── .env.example
└── README.md
```

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. ✍️ Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 🚀 Push to the branch (`git push origin feature/amazing-feature`)
5. 🎉 Open a Pull Request

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
CHANNEL_NAME=target_channel_name
DATABASE_URL=sqlite:///data/telegram.db
```

## 📈 Performance

- ⚡ Asynchronous message fetching
- 🗄️ Efficient SQLite database storage
- 📊 Progress tracking and statistics
- 🚦 Rate limiting support

## 🧪 Testing

The project includes a comprehensive test suite using pytest. The tests cover the following components:

- 🔄 **Models**: Database model validation and operations
- 🌐 **Service Layer**: Message processing and media handling
- 📡 **Telegram Client**: Connection, message fetching, and media downloads

To run the tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src tests/
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_models.py       # Database model tests
├── test_service.py      # Service layer tests
└── test_telegram_client.py  # Telegram client tests
```

Each test module focuses on a specific component of the application, ensuring proper functionality and error handling.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ by @Rantoniaina
</div>
