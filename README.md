# Telegram Message Fetcher

A robust Python application for fetching and storing messages from Telegram channels. Built with modern best practices and a clean architecture.

## Features

- Fetch messages from Telegram channels
- Download and store media files
- Store messages in SQLite database
- CLI interface with rich formatting
- Async support for better performance
- Comprehensive logging
- Type hints and documentation

## Prerequisites

- Python 3.8 or higher
- Telegram API credentials (API ID and Hash)
- Access to the target Telegram channel

## Installation

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

## Usage

The application provides a CLI interface with the following commands:

### Fetch Messages

To fetch messages from the configured channel:

```bash
python -m src.cli fetch
```

Options:

- `--limit INTEGER`: Limit the number of messages to fetch

### List Messages

To list stored messages:

```bash
python -m src.cli list
```

Options:

- `--limit INTEGER`: Number of messages to display (default: 100)
- `--skip INTEGER`: Number of messages to skip (default: 0)

## Project Structure

```
telegram-fetcher/
├── src/
│   ├── __init__.py
│   ├── cli.py           # CLI interface
│   ├── config.py        # Configuration management
│   ├── models.py        # Database models
│   ├── service.py       # Business logic
│   └── telegram_client.py # Telegram client wrapper
├── data/
│   ├── media/          # Downloaded media files
│   └── telegram.db     # SQLite database
├── requirements.txt
├── .env.example
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
