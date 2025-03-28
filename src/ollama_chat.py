import typer
import httpx
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from typing import Optional

app = typer.Typer()
console = Console()

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def chat(self, prompt: str, model: str = "llava") -> str:
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
    model: str = typer.Option("llava", help="The Ollama model to use"),
    base_url: str = typer.Option("http://localhost:11434", help="Ollama API base URL")
):
    """Start an interactive chat session with Ollama LLaVa model."""
    console.print("[bold green]Starting chat with Ollama LLaVa...[/bold green]")
    console.print("Type 'exit' or press Ctrl+C to end the chat.\n")
    
    client = OllamaClient(base_url)
    
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