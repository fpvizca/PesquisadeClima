import os
from datetime import datetime, timedelta
from db import get_db, init_db, init_app
from auth import hash_senha, usuario_logado, has_role
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
    result = dict(now=datetime.now(), has_role=has_role, is_admin=False)
    if 'usuario_id' in session:
        result['is_admin'] = has_role(session['usuario_id'], 'admin')
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

    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE (email = ? OR login = ?) AND ativo = 1", (login_input, login_input)).fetchone()
    if user and user['senha_hash'] == hash_senha(senha):
        session.permanent = True
        session['usuario_id'] = user['id']
        session['usuario_nome'] = user['nome']
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('pesquisa'))
    flash('Usuário ou senha inválidos.', 'danger')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None)
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
        db = get_db()
        db.commit()
    app.run(debug=os.environ.get('DEBUG', 'true').lower() == 'true', port=5005)
