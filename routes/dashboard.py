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
        total_perguntas = db.execute(
            "SELECT COUNT(*) as c FROM perguntas WHERE secao_id IN (SELECT id FROM secoes WHERE ativo = 1)"
        ).fetchone()['c']
        total_respostas = 0
        if ciclo_atual:
            total_respostas = db.execute(
                "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ?",
                (ciclo_atual['id'],)
            ).fetchone()['c']

        return render_template('dashboard.html', user=user,
            ciclo_atual=ciclo_atual,
            total_perguntas=total_perguntas,
            total_respostas=total_respostas
        )
