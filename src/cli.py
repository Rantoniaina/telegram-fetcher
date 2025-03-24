import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm
from loguru import logger
import sys
import subprocess
import os
from pathlib import Path
from .models import init_db, get_db
from .service import MessageService
from .config import settings
from .cleanup import CleanupService
from .normalization import NormalizationService

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


@app.command()
def cleanup(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    database_only: bool = typer.Option(False, "--database-only", help="Clean up only the database records"),
    media_only: bool = typer.Option(False, "--media-only", help="Clean up only the media files"),
    message_type: str = typer.Option(None, "--message-type", help="Type of messages to clean ('messages' or 'normalized'). Only valid with --database-only")
):
    """Clear data (messages and/or media files)."""
    try:
        if message_type and not database_only:
            console.print("[yellow]--message-type option is only valid with --database-only[/yellow]")
            return
            
        if message_type and message_type not in ['messages', 'normalized']:
            console.print("[yellow]--message-type must be either 'messages' or 'normalized'[/yellow]")
            return
            
        if database_only and media_only:
            console.print("[yellow]Cannot use both --database-only and --media-only[/yellow]")
            return

        operation = "all data"
        if database_only:
            operation = f"{message_type or 'all'} database records"
        elif media_only:
            operation = "media files"

        if not force and not Confirm.ask(f"[bold red]This will delete {operation}. Are you sure?[/bold red]"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return

        db = next(get_db())
        cleanup_service = CleanupService(db)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task("Cleaning up...", total=None)
            success = cleanup_service.cleanup_all(
                database_only=database_only,
                media_only=media_only,
                message_type=message_type
            )
        
        if success:
            console.print(f"[bold green]Successfully cleared {operation}![/bold green]")
        else:
            console.print("[bold red]Some errors occurred during cleanup[/bold red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def normalize(
    limit: int = typer.Option(None, help="Maximum number of messages to normalize in each batch"),
    skip_empty: bool = typer.Option(False, help="Skip normalizing messages with empty text"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress for each message")
):
    """Normalize stored messages."""
    try:
        db = next(get_db())
        service = NormalizationService(db)
        
        console.print("[bold green]Starting message normalization...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            disable=not verbose
        ) as progress:
            task = progress.add_task("Normalizing messages...", total=None)
            normalized_count = service.normalize_messages(
                batch_size=limit or 100
            )
            if verbose:
                progress.update(task, completed=normalized_count, total=normalized_count)
        
        console.print(f"[bold green]Normalization completed! {normalized_count} messages normalized.[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def init():
    """Initialize the project by setting up database, required directories, and Docker services."""
    try:
        # Create media directory if it doesn't exist
        media_path = Path(settings.MEDIA_PATH)
        if not media_path.exists():
            media_path.mkdir(parents=True)
            console.print(f"[green]Created media directory at {media_path}[/green]")
        
        # Initialize database
        init_db()
        console.print("[green]Database initialized successfully![/green]")
        
        # Check if Docker Compose services are running
        import subprocess
        try:
            # Check if containers are running
            result = subprocess.run(['docker-compose', 'ps', '-q'], capture_output=True, text=True)
            if not result.stdout.strip():
                console.print("[yellow]Docker Compose services are not running. Starting them now...[/yellow]")
                subprocess.run(['docker-compose', 'up', '-d'], check=True)
                console.print("[green]Docker Compose services started successfully![/green]")
            else:
                console.print("[green]Docker Compose services are already running.[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Could not check/start Docker Compose services: {e}[/yellow]")
        except FileNotFoundError:
            console.print("[yellow]Warning: Docker Compose not found. Please ensure Docker is installed.[/yellow]")
        
        console.print("[bold green]Project initialization completed! You can now start using the application.[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error during initialization: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def stop(
    clear_database: bool = typer.Option(False, "--clear-database", help="Clear database before stopping"),
    clear_media: bool = typer.Option(False, "--clear-media", help="Clear media files before stopping")
):
    """Stop Docker services."""
    try:
        if clear_database or clear_media:
            db = next(get_db())
            cleanup_service = CleanupService(db)
            success = cleanup_service.cleanup_all(
                database_only=clear_database and not clear_media,
                media_only=clear_media and not clear_database
            )
            if not success:
                console.print("[bold red]Some errors occurred during cleanup[/bold red]")
                raise typer.Exit(1)

        # Stop Docker services
        subprocess.run(['docker-compose', 'down'], check=True)
        console.print("[bold green]Services stopped successfully![/bold green]")
        
    except FileNotFoundError:
        console.print("[yellow]Docker Compose not found. Make sure Docker is installed.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()