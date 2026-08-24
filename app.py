import os
from datetime import datetime, timedelta
from db import get_db, init_db, init_app
from auth import hash_senha, api_request, upsert_usuario_externo, usuario_logado, has_role
from flask import Flask, render_template, request, redirect, session, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clima_vizca_secret_key_change_in_production')
app.permanent_session_lifetime = timedelta(minutes=20)
init_app(app)

from routes import init_all_routes
init_all_routes(app)

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('erro.html', codigo=404, mensagem='Página não encontrada.'), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template('erro.html', codigo=500, mensagem='Erro interno do servidor.'), 500

@app.context_processor
def inject_globals():
    result = dict(now=datetime.now(), today=datetime.now().strftime('%Y%m%d'), has_role=has_role, is_admin=False, is_gestor=False, is_diretoria=False)
    if 'usuario_id' in session:
        db = get_db()
        user_id = session['usuario_id']
        result['is_admin'] = has_role(user_id, 'admin')
        result['is_gestor'] = has_role(user_id, 'gestor')
        result['is_diretoria'] = has_role(user_id, 'diretoria')
    return result

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('pesquisa'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    login_input = request.form.get('login', '').strip()
    senha = request.form.get('senha', '')
    if not login_input:
        flash('Informe o usuário.', 'danger')
        return redirect(url_for('index'))

    # Tenta autenticar via API externa primeiro
    api_result = api_request('POST', '/auth/login', {'login': login_input, 'password': senha})
    if api_result.get('success') and api_result.get('user'):
        user_data = api_result['user']
        db = get_db()
        usuario_id = upsert_usuario_externo(user_data)
        user = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if user and user['ativo']:
            session.permanent = True
            session['usuario_id'] = user['id']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        flash('Usuário desativado.', 'danger')
        return redirect(url_for('index'))

    # Fallback: autenticação local (desenvolvimento)
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE (email = ? OR login = ?) AND ativo = 1", (login_input, login_input)).fetchone()
    if user and user['senha_hash'] == hash_senha(senha):
        session.permanent = True
        session['usuario_id'] = user['id']
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    flash('Usuário ou senha inválidos.', 'danger')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
        db = get_db()
        db.commit()
    app.run(debug=os.environ.get('DEBUG', 'true').lower() == 'true', port=5005)
