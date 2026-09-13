from flask import render_template, request, redirect, session, url_for, flash
from auth import login_required, has_role
from db import get_db

def init_routes(app):

    @app.route('/admin/formularios')
    @login_required
    def admin_formularios():
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        formularios = db.execute("""
            SELECT f.*, COUNT(DISTINCT s.id) as total_secoes,
                   COUNT(DISTINCT p.id) as total_perguntas
            FROM formularios f
            LEFT JOIN secoes s ON s.formulario_id = f.id AND s.ativo = 1
            LEFT JOIN perguntas p ON p.secao_id = s.id AND p.ativo = 1
            GROUP BY f.id
            ORDER BY f.nome
        """).fetchall()

        return render_template('admin_formularios.html', formularios=formularios)

    @app.route('/admin/formularios/novo', methods=['GET', 'POST'])
    @login_required
    def admin_formulario_novo():
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()

            if not nome:
                flash('Nome do formulário é obrigatório.', 'danger')
                return redirect(url_for('admin_formulario_novo'))

            db.execute(
                "INSERT INTO formularios (nome, descricao) VALUES (?, ?)",
                (nome, descricao or None)
            )
            db.commit()
            flash('Formulário criado com sucesso!', 'success')
            return redirect(url_for('admin_formularios'))

        return render_template('admin_formulario_form.html', formulario=None)

    @app.route('/admin/formularios/<int:formulario_id>/editar', methods=['GET', 'POST'])
    @login_required
    def admin_formulario_editar(formulario_id):
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        formulario = db.execute("SELECT * FROM formularios WHERE id = ?", (formulario_id,)).fetchone()
        if not formulario:
            flash('Formulário não encontrado.', 'warning')
            return redirect(url_for('admin_formularios'))

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            ativo = 1 if request.form.get('ativo') else 0

            if not nome:
                flash('Nome do formulário é obrigatório.', 'danger')
                return redirect(url_for('admin_formulario_editar', formulario_id=formulario_id))

            db.execute(
                "UPDATE formularios SET nome = ?, descricao = ?, ativo = ? WHERE id = ?",
                (nome, descricao or None, ativo, formulario_id)
            )
            db.commit()
            flash('Formulário atualizado com sucesso!', 'success')
            return redirect(url_for('admin_formularios'))

        return render_template('admin_formulario_form.html', formulario=formulario)

    @app.route('/admin/formularios/<int:formulario_id>/excluir', methods=['POST'])
    @login_required
    def admin_formulario_excluir(formulario_id):
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        formulario = db.execute("SELECT * FROM formularios WHERE id = ?", (formulario_id,)).fetchone()
        if not formulario:
            flash('Formulário não encontrado.', 'warning')
            return redirect(url_for('admin_formularios'))

        # Verificar se há ciclos vinculados
        tem_ciclos = db.execute(
            "SELECT COUNT(*) as c FROM ciclos WHERE formulario_id = ?", (formulario_id,)
        ).fetchone()['c']

        if tem_ciclos > 0:
            flash(f'Não é possível excluir: o formulário possui {tem_ciclos} ciclo(s) vinculado(s).', 'danger')
            return redirect(url_for('admin_formularios'))

        db.execute("DELETE FROM formularios WHERE id = ?", (formulario_id,))
        db.commit()
        flash('Formulário excluído com sucesso!', 'success')
        return redirect(url_for('admin_formularios'))

    @app.route('/admin/formularios/<int:formulario_id>/duplicar', methods=['POST'])
    @login_required
    def admin_formulario_duplicar(formulario_id):
        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        formulario = db.execute("SELECT * FROM formularios WHERE id = ?", (formulario_id,)).fetchone()
        if not formulario:
            flash('Formulário não encontrado.', 'warning')
            return redirect(url_for('admin_formularios'))

        # Criar cópia do formulário
        novo_nome = f"{formulario['nome']} (Cópia)"
        cursor = db.execute(
            "INSERT INTO formularios (nome, descricao, ativo) VALUES (?, ?, 0)",
            (novo_nome, formulario['descricao'])
        )
        novo_formulario_id = cursor.lastrowid

        # Copiar seções
        secoes = db.execute(
            "SELECT * FROM secoes WHERE formulario_id = ? AND ativo = 1 ORDER BY ordem",
            (formulario_id,)
        ).fetchall()

        for secao in secoes:
            cursor_secao = db.execute(
                "INSERT INTO secoes (formulario_id, nome, descricao, ordem, ativo) VALUES (?, ?, ?, ?, ?)",
                (novo_formulario_id, secao['nome'], secao['descricao'], secao['ordem'], secao['ativo'])
            )
            nova_secao_id = cursor_secao.lastrowid

            # Copiar perguntas
            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 ORDER BY ordem",
                (secao['id'],)
            ).fetchall()

            for pergunta in perguntas:
                db.execute(
                    """INSERT INTO perguntas (secao_id, codigo, texto, descricao, tipo, obrigatoria,
                       opcoes, grid_rows, ordem, ativo, condicional, condicao_pergunta, condicao_valor)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (nova_secao_id, pergunta['codigo'], pergunta['texto'], pergunta['descricao'],
                     pergunta['tipo'], pergunta['obrigatoria'], pergunta['opcoes'], pergunta['grid_rows'],
                     pergunta['ordem'], pergunta['ativo'], pergunta['condicional'],
                     pergunta['condicao_pergunta'], pergunta['condicao_valor'])
                )

        db.commit()
        flash(f'Formulário duplicado com sucesso! {len(secoes)} seções copiadas.', 'success')
        return redirect(url_for('admin_formularios'))
