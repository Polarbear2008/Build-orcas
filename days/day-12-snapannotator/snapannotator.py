import cv2
import urllib.request
import json
import base64
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown

console = Console()
MODEL_NAME = "moondream"

def check_vision_model():
    """Validates that the edge VLM specified in the Pre-Launch Checklist is resident."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            models = [m["name"] for m in json.loads(resp.read()).get("models", [])]
            if not any(MODEL_NAME in m for m in models):
                console.print(f"[red]Error: {MODEL_NAME} VLM not found. Run 'ollama pull moondream'[/red]")
                sys.exit(1)
            return True
    except:
        console.print("[red]Error: Ollama daemon not found on localhost:11434[/red]")
        sys.exit(1)

def capture_image():
    """Accesses the raw optical sensor and warms the hardware exposure."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        console.print("[red]Error: Optical sensor access denied.[/red]")
        sys.exit(1)
        
    console.print("[yellow]Engaging optical sensor. Calibrating exposure...[/yellow]")
    
    for i in range(3, 0, -1):
        console.print(f" ▸ Snapping in {i}...")
        start = time.time()
        while time.time() - start < 1.0:
            cap.read() 
            
    # Final capture slice
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        console.print("[red]Error: Sensor failed to return payload.[/red]")
        sys.exit(1)
        
    console.print("[green]Frame generated successfully.[/green]")
    console.print("[dim]Aggressively downscaling optical matrix for blazing fast inference...[/dim]\n")
    

    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
    return base64.b64encode(buffer).decode('utf-8')

def analyze_image(img_b64):
    """Pumps the Base64 image payload into the Moondream VLM layer."""
    prompt = "Analyze this image and list every single object, person, or element you can explicitly identify. Be highly observant and concise."
    
    data = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [img_b64],
        "stream": True
    }).encode('utf-8')
    
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data)
    
    full_text = ""
    
    with Live(Panel("[yellow]Initializing Moondream Vision Core... (This may take 10-15 seconds depending on hardware)[/yellow]", border_style="blue"), refresh_per_second=15) as live:
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                for line in resp:
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            full_text += chunk["response"]
                            live.update(Panel(Markdown(full_text), title=f"SnapAnnotator [{MODEL_NAME}]", border_style="cyan"))
        except Exception as e:
            live.update(Panel(f"[red]Inference network failed: {e}[/red]", title="Error"))

def main():
    console.print("[bold cyan]SnapAnnotator Edge Vision Core[/bold cyan]")
    check_vision_model()
    
    console.print("Press [bold white]ENTER[/bold white] to engage the optical sensor and analyze surroundings, or type 'quit'.")
    
    while True:
        try:
            cmd = input("\nReady > ")
            if cmd.lower() in ['quit', 'exit', 'q']: break
            
            img_b64 = capture_image()
            analyze_image(img_b64)
            
        except KeyboardInterrupt:
            break
            
    console.print("\n[dim]Optical connection severed.[/dim]")

if __name__ == "__main__":
    main()
