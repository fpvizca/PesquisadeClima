import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from db import get_db, init_app
from auth import hash_senha, api_request, upsert_usuario_externo, usuario_logado, has_role, usuario_bloqueado, mensagem_bloqueio
from flask import Flask, render_template, request, redirect, session, url_for, flash

SECRET_KEY_PADRAO = 'clima_vizca_secret_key_change_in_production'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or SECRET_KEY_PADRAO
app.permanent_session_lifetime = timedelta(minutes=int(os.environ.get('SESSION_MINUTES', '20')))
init_app(app)

_chave = app.secret_key
if _chave == SECRET_KEY_PADRAO or len(str(_chave)) < 32:
    print('AVISO: SECRET_KEY ausente, fraca ou igual ao padrao.')
    print('       Sessions ficam inseguras e cao a cada reinicio.')
    print('       Defina SECRET_KEY no arquivo .env antes de publicar.')

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
    result = dict(now=datetime.now(), today=datetime.now().strftime('%Y%m%d'), has_role=has_role, is_admin=False, is_gestor=False, is_diretoria=False, user=None)
    if 'usuario_id' in session:
        db = get_db()
        user_id = session['usuario_id']
        result['user'] = db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
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

    # Bloqueio de colaboradores fora do perfil da pesquisa
    bloq = usuario_bloqueado(login_input)
    if bloq:
        flash(mensagem_bloqueio(), 'danger')
        return redirect(url_for('index'))

    # Autenticação via API externa
    api_result = api_request('POST', '/auth/login', {'login': login_input, 'password': senha})
    if api_result.get('success') and api_result.get('user'):
        user_data = api_result['user']
        db = get_db()
        usuario_id = upsert_usuario_externo(user_data)
        user = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if user and user['ativo']:
            if usuario_bloqueado(user['login']):
                flash(mensagem_bloqueio(), 'danger')
                return redirect(url_for('index'))
            session.permanent = True
            session['usuario_id'] = user['id']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        flash('Usuário desativado.', 'danger')
        return redirect(url_for('index'))

    # Fallback local (quando API indisponível)
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE (email = ? OR login = ?) AND ativo = 1", (login_input, login_input)).fetchone()
    if user and user['senha_hash'] == hash_senha(senha):
        if usuario_bloqueado(user['login'] or login_input):
            flash(mensagem_bloqueio(), 'danger')
            return redirect(url_for('index'))
        session.permanent = True
        session['usuario_id'] = user['id']
        flash('Login realizado com sucesso! (modo local)', 'warning')
        return redirect(url_for('dashboard'))

    # Diagnostico: a API externa e a unica forma de validar a maioria dos usuarios
    if api_result.get('error') and user and user['senha_hash'] == 'api_externo':
        flash('O servidor de autenticacao esta indisponivel no momento. '
              'Tente novamente em alguns minutos.', 'warning')
        return redirect(url_for('index'))

    if api_result.get('error') == 'Servidor externo indisponível':
        flash('Usuario ou senha invalidos. '
              'Aviso: o servidor de autenticacao esta indisponivel, '
              'o que pode impedir o acesso de usuarios externos.', 'warning')
        return redirect(url_for('index'))

    flash('Usuário ou senha inválidos.', 'danger')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    from migrar import aplicar
    aplicar()

    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    porta = int(os.environ.get('PORT', '5005'))
    app.run(debug=debug, host=os.environ.get('HOST', '127.0.0.1'), port=porta)
