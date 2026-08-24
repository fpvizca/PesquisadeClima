import hashlib
from flask import session
from db import get_db

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def usuario_logado():
    if 'usuario_id' in session:
        db = get_db()
        user = db.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],)).fetchone()
        if user:
            return user
        session.pop('usuario_id', None)
    return None

def has_role(usuario_id, role):
    db = get_db()
    r = db.execute("SELECT 1 FROM usuario_roles WHERE usuario_id = ? AND role = ?", (usuario_id, role)).fetchone()
    return r is not None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            from flask import redirect, url_for, flash
            flash('Faça login para acessar.', 'warning')
            return redirect(url_for('index'))
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
        if not has_role(session['usuario_id'], 'admin'):
            from flask import redirect, url_for, flash
            flash('Acesso negado. Apenas administradores.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function
