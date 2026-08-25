from flask import render_template, request, redirect, session, url_for, flash
from auth import login_required, has_role
from db import get_db

def init_routes(app):

    @app.route('/admin/ciclos')
    @login_required
    def admin_ciclos():
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        ciclos = db.execute("""
            SELECT c.*, f.nome as formulario_nome
            FROM ciclos c
            LEFT JOIN formularios f ON c.formulario_id = f.id
            ORDER BY c.ano DESC, c.id DESC
        """).fetchall()

        formularios = db.execute("SELECT * FROM formularios ORDER BY nome").fetchall()
        return render_template('admin_ciclos.html', ciclos=ciclos, formularios=formularios)

    @app.route('/admin/ciclos/novo', methods=['GET', 'POST'])
    @login_required
    def admin_ciclo_novo():
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        formularios = db.execute("SELECT * FROM formularios ORDER BY nome").fetchall()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            ano = request.form.get('ano', '').strip()
            formulario_id = request.form.get('formulario_id', type=int)
            data_inicio = request.form.get('data_inicio', '').strip()
            data_fim = request.form.get('data_fim', '').strip()
            ativo = 1 if request.form.get('ativo') else 0

            if not nome or not ano:
                flash('Nome e Ano são obrigatórios.', 'danger')
                return redirect(url_for('admin_ciclo_novo'))

            # Se ativar, desativar outros ciclos
            if ativo:
                db.execute("UPDATE ciclos SET ativo = 0")

            db.execute(
                "INSERT INTO ciclos (nome, ano, formulario_id, data_inicio, data_fim, ativo) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, int(ano), formulario_id, data_inicio or None, data_fim or None, ativo)
            )
            db.commit()
            flash('Ciclo criado com sucesso!', 'success')
            return redirect(url_for('admin_ciclos'))

        return render_template('admin_ciclo_form.html', ciclo=None, formularios=formularios)

    @app.route('/admin/ciclos/<int:ciclo_id>/editar', methods=['GET', 'POST'])
    @login_required
    def admin_ciclo_editar(ciclo_id):
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        ciclo = db.execute("SELECT * FROM ciclos WHERE id = ?", (ciclo_id,)).fetchone()
        if not ciclo:
            flash('Ciclo não encontrado.', 'warning')
            return redirect(url_for('admin_ciclos'))

        formularios = db.execute("SELECT * FROM formularios ORDER BY nome").fetchall()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            ano = request.form.get('ano', '').strip()
            formulario_id = request.form.get('formulario_id', type=int)
            data_inicio = request.form.get('data_inicio', '').strip()
            data_fim = request.form.get('data_fim', '').strip()
            ativo = 1 if request.form.get('ativo') else 0

            if not nome or not ano:
                flash('Nome e Ano são obrigatórios.', 'danger')
                return redirect(url_for('admin_ciclo_editar', ciclo_id=ciclo_id))

            # Se ativar, desativar outros ciclos
            if ativo and not ciclo['ativo']:
                db.execute("UPDATE ciclos SET ativo = 0 WHERE id != ?", (ciclo_id,))

            db.execute(
                "UPDATE ciclos SET nome = ?, ano = ?, formulario_id = ?, data_inicio = ?, data_fim = ?, ativo = ? WHERE id = ?",
                (nome, int(ano), formulario_id, data_inicio or None, data_fim or None, ativo, ciclo_id)
            )
            db.commit()
            flash('Ciclo atualizado com sucesso!', 'success')
            return redirect(url_for('admin_ciclos'))

        return render_template('admin_ciclo_form.html', ciclo=ciclo, formularios=formularios)

    @app.route('/admin/ciclos/<int:ciclo_id>/excluir', methods=['POST'])
    @login_required
    def admin_ciclo_excluir(ciclo_id):
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        ciclo = db.execute("SELECT * FROM ciclos WHERE id = ?", (ciclo_id,)).fetchone()
        if not ciclo:
            flash('Ciclo não encontrado.', 'warning')
            return redirect(url_for('admin_ciclos'))

        # Verificar se há respostas
        tem_respostas = db.execute(
            "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ?", (ciclo_id,)
        ).fetchone()['c']

        if tem_respostas > 0:
            flash(f'Não é possível excluir: o ciclo possui {tem_respostas} respostas.', 'danger')
            return redirect(url_for('admin_ciclos'))

        db.execute("DELETE FROM ciclos WHERE id = ?", (ciclo_id,))
        db.commit()
        flash('Ciclo excluído com sucesso!', 'success')
        return redirect(url_for('admin_ciclos'))

    @app.route('/admin/ciclos/<int:ciclo_id>/ativar', methods=['POST'])
    @login_required
    def admin_ciclo_ativar(ciclo_id):
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db.execute("UPDATE ciclos SET ativo = 0")
        db.execute("UPDATE ciclos SET ativo = 1 WHERE id = ?", (ciclo_id,))
        db.commit()
        flash('Ciclo ativado com sucesso!', 'success')
        return redirect(url_for('admin_ciclos'))
