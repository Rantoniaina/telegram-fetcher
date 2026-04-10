import typer
import httpx
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = typer.Typer()
console = Console()

class OllamaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = httpx.Client(timeout=30.0)
    
    def check_health(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = self.client.get(f"{self.base_url}/api/version")
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    def chat(self, prompt: str, model: str = None) -> str:
        model = model or os.getenv("OLLAMA_MODEL", "llava")
        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error: {str(e)}"

@app.command()
def chat(
    model: str = typer.Option(None, help="The Ollama model to use (overrides OLLAMA_MODEL env var)"),
    base_url: str = typer.Option(None, help="Ollama API base URL (overrides OLLAMA_BASE_URL env var)")
):
    """Start an interactive chat session with Ollama LLaVa model."""
    client = OllamaClient(base_url)
    
    # Check if Ollama service is available
    if not client.check_health():
        console.print("[bold red]Error: Ollama service is not available. Please make sure it's running.[/bold red]")
        raise typer.Exit(1)
    
    console.print("[bold green]Starting chat with Ollama LLaVa...[/bold green]")
    console.print("Type 'exit' or press Ctrl+C to end the chat.\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            if user_input.lower() == "exit":
                break
            
            console.print("[bold yellow]Assistant[/bold yellow]")
            response = client.chat(user_input, model)
            console.print(Markdown(response))
            console.print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            break
    
    console.print("\n[bold green]Chat session ended. Goodbye![/bold green]")

def main():
    app()

if __name__ == "__main__":
    main()