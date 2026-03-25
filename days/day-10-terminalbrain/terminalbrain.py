import sys
import subprocess
import urllib.request
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

console = Console()

def get_best_model():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req) as resp:
            models = [m["name"] for m in json.loads(resp.read()).get("models", [])]
            for m in models:
                if any(x in m.lower() for x in ['qwen', 'llama', 'phi', 'mistral', 'gemma']):
                    return m
            return models[0] if models else None
    except:
        return None

def analyze_error_stream(cmd, error_text, model):
    prompt = (
        f"The terminal command `{cmd}` failed with the following stderr output:\n\n"
        f"```\n{error_text.strip()}\n```\n\n"
        f"Explain exactly why it failed in one concise sentence. Then provide ONLY the exact code or command to fix it. No yapping. No conversational text."
    )
    
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": True
    }).encode('utf-8')
    
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data)
    
    try:
        with urllib.request.urlopen(req) as resp:
            full_text = ""
            with Live(Panel(Markdown("thinking..."), title="🧠 TerminalBrain Interface", border_style="green"), refresh_per_second=15) as live:
                for line in resp:
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            full_text += chunk["response"]
                            live.update(Panel(Markdown(full_text), title="🧠 TerminalBrain Interface", border_style="green"))
    except Exception as e:
        console.print(f"Error contacting local AI: {e}")

def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage: python terminalbrain.py '<command>'[/bold red]")
        sys.exit(1)
        
    cmd = " ".join(sys.argv[1:])
    
    process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, text=True)
    _, stderr_text = process.communicate()
    
    if stderr_text:
        sys.stderr.write(stderr_text)
        
    if process.returncode != 0:
        model = get_best_model()
        if not model:
            console.print("\n[bold red]TerminalBrain:[/bold red] Error detected, but Ollama server is offline.")
            sys.exit(1)
            
        console.print(f"\n[bold yellow]TerminalBrain ([/bold yellow][cyan]{model}[/cyan][bold yellow]) intercepting exception...[/bold yellow]")
        
        analyze_error_stream(cmd, stderr_text, model)

if __name__ == "__main__":
    main()
