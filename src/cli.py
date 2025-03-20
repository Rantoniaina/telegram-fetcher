import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from loguru import logger
import sys

from .models import init_db, get_db
from .service import MessageService
from .config import settings

app = typer.Typer()
console = Console()

# Configure logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <white>{message}</white>")


@app.command()
def fetch(
    limit: int = typer.Option(None, help="Limit the number of messages to fetch"),
    no_media: bool = typer.Option(False, help="Skip downloading media files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress for each message")
):
    """Fetch messages from the Telegram channel."""
    try:
        init_db()
        db = next(get_db())
        service = MessageService(db)
        
        console.print("[bold green]Starting message fetch...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            disable=not verbose
        ) as progress:
            task = progress.add_task("Initializing...", total=None)
            asyncio.run(service.process_messages(
                limit=limit,
                download_media=not no_media,
                progress_callback=lambda msg, current, total: progress.update(
                    task,
                    completed=current,
                    total=total,
                    description=f"Message {current}/{total}: {msg.text[:30] + '...' if msg.text else 'No text'}"
                ) if verbose else None
            ))
            
        console.print("[bold green]Message fetch completed![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def list(
    limit: int = typer.Option(100, help="Number of messages to display"),
    skip: int = typer.Option(0, help="Number of messages to skip"),
):
    """List stored messages."""
    try:
        db = next(get_db())
        service = MessageService(db)
        messages = service.get_messages(skip=skip, limit=limit)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Date")
        table.add_column("Text")
        table.add_column("Media")
        
        for msg in messages:
            table.add_row(
                str(msg.message_id),
                str(msg.date),
                (msg.text[:50] + "...") if msg.text and len(msg.text) > 50 else str(msg.text),
                "✓" if msg.media_path else "✗"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 