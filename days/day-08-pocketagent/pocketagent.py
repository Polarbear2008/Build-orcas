import json
import urllib.request
import urllib.error
import sys

def check_server():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return [m["name"] for m in data.get("models", [])]
    except urllib.error.URLError:
        return None

def chat(prompt, model):
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": True
    }).encode('utf-8')
    
    req = urllib.request.Request("http://localhost:11434/api/generate", data=data)
    try:
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        print(chunk["response"], end='', flush=True)
            print()
    except Exception as e:
        print(f"Error: {e}")

def main():
    models = check_server()
    if not models:
        print("Ollama server down or no models found.")
        sys.exit(1)
        
    model = models[0]
    for m in models:
        if any(x in m.lower() for x in ['qwen', 'llama', 'phi', 'mistral', 'gemma']):
            model = m
            break
            
    print(f"Loaded {model}")
    
    while True:
        try:
            val = input("\n> ")
            if val.lower() in ['exit', 'quit']:
                break
                
            chat(val, model)
            
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
