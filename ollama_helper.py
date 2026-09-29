import json
import time
import hashlib
import urllib.request
import urllib.error
import os

OLLAMA_BASE = os.environ.get('OLLAMA_BASE', 'http://192.168.170.12:11434')
MODEL = os.environ.get('OLLAMA_MODEL', 'ministral-3:8b')

# Timeout por chamada. Gerar analise de um modelo 8b pode demorar, mas o
# export Word faz ~90 chamadas: um timeout alto transforma o export em horas.
TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '20'))

# Cache em memoria por prompt: evita regenerar a mesma analise e torna
# reexports consecutivos instantaneos.
CACHE_MAX = int(os.environ.get('OLLAMA_CACHE_MAX', '300'))

# Circuit breaker: apos uma falha, as proximas chamadas falham na hora em vez
# de esperar o timeout uma por uma.
COOLDOWN = int(os.environ.get('OLLAMA_COOLDOWN', '60'))

_cache = {}
_indisponivel_ate = 0.0
_ultimo_erro = ''


def limpar_cache():
    global _indisponivel_ate, _ultimo_erro
    _cache.clear()
    _indisponivel_ate = 0.0
    _ultimo_erro = ''


def indisponivel():
    return time.time() < _indisponivel_ate


def generate(prompt, model=None):
    global _indisponivel_ate, _ultimo_erro

    model = model or MODEL
    chave = hashlib.sha256((model + '\n' + prompt).encode('utf-8')).hexdigest()

    if chave in _cache:
        return _cache[chave]

    if indisponivel():
        return _ultimo_erro or 'Erro ao conectar com Ollama: servico indisponivel no momento.'

    url = f"{OLLAMA_BASE}/api/generate"
    data = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            texto = result.get('response', '')
            _indisponivel_ate = 0.0
            if len(_cache) < CACHE_MAX:
                _cache[chave] = texto
            return texto
    except urllib.error.URLError as e:
        _ultimo_erro = f"Erro ao conectar com Ollama: {str(e)}"
    except Exception as e:
        _ultimo_erro = f"Erro ao gerar resposta: {str(e)}"

    _indisponivel_ate = time.time() + COOLDOWN
    return _ultimo_erro
