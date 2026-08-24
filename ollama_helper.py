import json
import urllib.request
import urllib.error
import os

OLLAMA_BASE = os.environ.get('OLLAMA_BASE', 'http://localhost:11434')
MODEL = os.environ.get('OLLAMA_MODEL', 'ministral-3:8b')

def generate(prompt, model=None):
    model = model or MODEL
    url = f"{OLLAMA_BASE}/api/generate"
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result.get('response', '')
    except urllib.error.URLError as e:
        return f"Erro ao conectar com Ollama: {str(e)}"
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"
