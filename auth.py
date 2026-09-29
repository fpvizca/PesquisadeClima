import hashlib
import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from flask import session
from db import get_db

API_BASE = os.environ.get('API_BASE', 'https://relats.vizca.com.br')

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def api_request(method, path, data=None):
    url = API_BASE + path
    headers = {'Content-Type': 'application/json'}
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode('utf-8'))
        except Exception:
            return {'error': f'HTTP {e.code}'}
    except urllib.error.URLError:
        return {'error': 'Servidor externo indisponível'}

def upsert_usuario_externo(user_data):
    db = get_db()
    ext_id = user_data['id']
    login = user_data.get('login', '')
    nome = user_data.get('name', '')
    email = user_data.get('email') or f'{login}@externo.local'
    local = db.execute("SELECT id FROM usuarios WHERE id_externo = ?", (ext_id,)).fetchone()
    if local:
        db.execute("""
            UPDATE usuarios SET login = ?, nome = ?, email = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (login, nome, email, local['id']))
        db.commit()
        return local['id']
    else:
        c = db.execute("""
            INSERT INTO usuarios (nome, email, login, id_externo, senha_hash)
            VALUES (?, ?, ?, ?, 'api_externo')
        """, (nome, email, login, ext_id))
        db.commit()
        return c.lastrowid

def usuario_bloqueado(login):
    if not login:
        return None
    db = get_db()
    return db.execute(
        "SELECT * FROM usuarios_bloqueados WHERE lower(login) = lower(?)",
        (login.strip(),)
    ).fetchone()

def mensagem_bloqueio(ano=None):
    if not ano:
        ano = os.environ.get('ANO_PESQUISA')
    if not ano:
        try:
            db = get_db()
            row = db.execute(
                "SELECT ano FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1"
            ).fetchone()
            ano_atual = datetime.now().year
            ano = row['ano'] if row and row['ano'] >= ano_atual else ano_atual
        except Exception:
            ano = None
    ano = ano or datetime.now().year
    return (f'A pesquisa de clima VIZCA {ano} é direcionada para colaboradores com mais de '
            '3 meses de empresa. Os colaboradores que não estiverem nesta situação poderão '
            'participar da próxima pesquisa.')

def _eh_bloqueado(user):
    if not user or not user['login']:
        return False
    db = get_db()
    return db.execute(
        "SELECT 1 FROM usuarios_bloqueados WHERE lower(login) = lower(?)",
        (user['login'],)
    ).fetchone() is not None

def _encerrar_sessao_bloqueada():
    from flask import g, flash
    session.pop('usuario_id', None)
    if not getattr(g, '_bloqueio_notificado', False):
        g._bloqueio_notificado = True
        flash(mensagem_bloqueio(), 'danger')

def usuario_logado():
    if 'usuario_id' in session:
        db = get_db()
        user = db.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],)).fetchone()
        if user:
            if not _eh_bloqueado(user):
                return user
            _encerrar_sessao_bloqueada()
        else:
            session.pop('usuario_id', None)
    return None

def has_role(usuario_id, role):
    db = get_db()
    if role in ('admin', 'diretoria'):
        r = db.execute("SELECT 1 FROM usuario_roles WHERE usuario_id = ? AND role = ?", (usuario_id, role)).fetchone()
        return r is not None
    if role == 'gestor':
        r = db.execute("SELECT 1 FROM usuario_roles WHERE usuario_id = ? AND role = 'gestor'", (usuario_id,)).fetchone()
        return r is not None
    if role == 'colaborador':
        r = db.execute("SELECT 1 FROM usuario_roles WHERE usuario_id = ? AND role = 'colaborador'", (usuario_id,)).fetchone()
        return r is not None
    return False

def _bloqueado_no_cenario():
    from flask import redirect, url_for
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],)).fetchone()
    if not user:
        return None
    if _eh_bloqueado(user):
        _encerrar_sessao_bloqueada()
        return redirect(url_for('index'))
    return None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            from flask import redirect, url_for, flash
            flash('Faça login para acessar.', 'warning')
            return redirect(url_for('index'))
        bloqueio = _bloqueado_no_cenario()
        if bloqueio is not None:
            return bloqueio
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            from flask import redirect, url_for, flash
            flash('Faça login para acessar.', 'warning')
            return redirect(url_for('index'))
        bloqueio = _bloqueado_no_cenario()
        if bloqueio is not None:
            return bloqueio
        if not has_role(session['usuario_id'], 'admin'):
            from flask import redirect, url_for, flash
            flash('Acesso negado. Apenas administradores.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
