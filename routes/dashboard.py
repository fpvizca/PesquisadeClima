from flask import render_template, redirect, url_for
from db import get_db
from auth import usuario_logado, has_role

def init_routes(app):
    @app.route('/dashboard')
    def dashboard():
        user = usuario_logado()
        if not user:
            return redirect(url_for('index'))
        db = get_db()
        is_admin = has_role(user['id'], 'admin')
        is_gestor = has_role(user['id'], 'gestor')
        is_diretoria = has_role(user['id'], 'diretoria')

        # Dados para o dashboard
        ciclo_atual = db.execute("SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1").fetchone()

        # Count questions from the cycle's form
        if ciclo_atual and ciclo_atual['formulario_id']:
            total_perguntas = db.execute(
                "SELECT COUNT(*) as c FROM perguntas WHERE secao_id IN (SELECT id FROM secoes WHERE formulario_id = ? AND ativo = 1)",
                (ciclo_atual['formulario_id'],)
            ).fetchone()['c']
            total_secoes = db.execute(
                "SELECT COUNT(*) as c FROM secoes WHERE formulario_id = ? AND ativo = 1",
                (ciclo_atual['formulario_id'],)
            ).fetchone()['c']
            primeira_secao = db.execute(
                "SELECT id FROM secoes WHERE formulario_id = ? AND ativo = 1 ORDER BY ordem LIMIT 1",
                (ciclo_atual['formulario_id'],)
            ).fetchone()
        else:
            total_perguntas = db.execute(
                "SELECT COUNT(*) as c FROM perguntas WHERE secao_id IN (SELECT id FROM secoes WHERE ativo = 1)"
            ).fetchone()['c']
            total_secoes = db.execute(
                "SELECT COUNT(*) as c FROM secoes WHERE ativo = 1"
            ).fetchone()['c']
            primeira_secao = db.execute(
                "SELECT id FROM secoes WHERE ativo = 1 ORDER BY ordem LIMIT 1"
            ).fetchone()

        primeira_secao_id = primeira_secao['id'] if primeira_secao else None

        total_respostas = 0
        ja_respondeu = False
        if ciclo_atual:
            total_respostas = db.execute(
                "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ?",
                (ciclo_atual['id'],)
            ).fetchone()['c']

            # Check if user has responded
            tem_respostas = db.execute(
                "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ? AND usuario_id = ?",
                (ciclo_atual['id'], user['id'])
            ).fetchone()['c']
            ja_respondeu = tem_respostas > 0

        return render_template('dashboard.html', user=user,
            ciclo_atual=ciclo_atual,
            total_perguntas=total_perguntas,
            total_secoes=total_secoes,
            total_respostas=total_respostas,
            ja_respondeu=ja_respondeu,
            primeira_secao_id=primeira_secao_id,
            is_admin=is_admin,
            is_gestor=is_gestor,
            is_diretoria=is_diretoria
        )
