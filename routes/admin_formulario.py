import json
from flask import render_template, request, redirect, flash, url_for, session
from auth import login_required, has_role
from db import get_db

def init_routes(app):

    def admin_required(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'usuario_id' not in session:
                flash('Faça login para acessar.', 'warning')
                return redirect(url_for('index'))
            if not has_role(session['usuario_id'], 'admin'):
                flash('Acesso negado.', 'danger')
                return redirect(url_for('pesquisa'))
            return f(*args, **kwargs)
        return decorated

    @app.route('/admin/formulario/<int:formulario_id>')
    @login_required
    def admin_formulario_estrutura(formulario_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        formulario = db.execute("SELECT * FROM formularios WHERE id = ?", (formulario_id,)).fetchone()
        if not formulario:
            flash('Formulário não encontrado.', 'warning')
            return redirect(url_for('admin_formularios'))

        secoes = db.execute(
            "SELECT * FROM secoes WHERE formulario_id = ? AND ativo = 1 ORDER BY ordem",
            (formulario_id,)
        ).fetchall()
        dados = []
        for secao in secoes:
            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 ORDER BY ordem",
                (secao['id'],)
            ).fetchall()
            dados.append({'secao': secao, 'perguntas': perguntas})

        return render_template('admin_formulario.html', dados=dados, formulario=formulario)

    @app.route('/admin/formulario/secao/nova/<int:formulario_id>', methods=['GET', 'POST'])
    @login_required
    def admin_secao_nova(formulario_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            ordem = request.form.get('ordem', 0, type=int)

            if not nome:
                flash('Nome é obrigatório.', 'danger')
                return redirect(url_for('admin_secao_nova', formulario_id=formulario_id))

            db.execute(
                "INSERT INTO secoes (formulario_id, nome, descricao, ordem) VALUES (?, ?, ?, ?)",
                (formulario_id, nome, descricao if descricao else None, ordem)
            )
            db.commit()
            flash('Seção criada com sucesso!', 'success')
            return redirect(url_for('admin_formulario_estrutura', formulario_id=formulario_id))

        max_ordem = db.execute(
            "SELECT COALESCE(MAX(ordem), 0) as m FROM secoes WHERE formulario_id = ?",
            (formulario_id,)
        ).fetchone()['m']
        return render_template('admin_secao_form.html', secao=None, max_ordem=max_ordem, formulario_id=formulario_id)

    @app.route('/admin/formulario/secao/<int:secao_id>/editar', methods=['GET', 'POST'])
    @login_required
    def admin_secao_editar(secao_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        secao = db.execute("SELECT * FROM secoes WHERE id = ?", (secao_id,)).fetchone()
        if not secao:
            flash('Seção não encontrada.', 'danger')
            return redirect(url_for('admin_formulario'))

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            ordem = request.form.get('ordem', 0, type=int)

            if not nome:
                flash('Nome é obrigatório.', 'danger')
                return redirect(url_for('admin_secao_editar', secao_id=secao_id))

            db.execute(
                "UPDATE secoes SET nome = ?, descricao = ?, ordem = ? WHERE id = ?",
                (nome, descricao if descricao else None, ordem, secao_id)
            )
            db.commit()
            flash('Seção atualizada com sucesso!', 'success')
            return redirect(url_for('admin_formulario_estrutura', formulario_id=secao['formulario_id']))

        return render_template('admin_secao_form.html', secao=secao, max_ordem=0, formulario_id=secao['formulario_id'])

    @app.route('/admin/formulario/secao/<int:secao_id>/excluir', methods=['POST'])
    @login_required
    def admin_secao_excluir(secao_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        secao = db.execute("SELECT formulario_id FROM secoes WHERE id = ?", (secao_id,)).fetchone()
        db.execute("UPDATE secoes SET ativo = 0 WHERE id = ?", (secao_id,))
        db.execute("UPDATE perguntas SET ativo = 0 WHERE secao_id = ?", (secao_id,))
        db.commit()
        flash('Seção excluída com sucesso!', 'success')
        return redirect(url_for('admin_formulario_estrutura', formulario_id=secao['formulario_id']))

    @app.route('/admin/formulario/secao/<int:secao_id>/duplicar', methods=['POST'])
    @login_required
    def admin_secao_duplicar(secao_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        secao = db.execute("SELECT * FROM secoes WHERE id = ?", (secao_id,)).fetchone()
        if not secao:
            flash('Seção não encontrada.', 'danger')
            return redirect(url_for('admin_formularios'))

        max_ordem = db.execute(
            "SELECT COALESCE(MAX(ordem), 0) as m FROM secoes WHERE formulario_id = ?",
            (secao['formulario_id'],)
        ).fetchone()['m']
        c = db.execute(
            "INSERT INTO secoes (formulario_id, nome, descricao, ordem) VALUES (?, ?, ?, ?)",
            (secao['formulario_id'], secao['nome'] + ' (Cópia)', secao['descricao'], max_ordem + 1)
        )
        nova_secao_id = c.lastrowid

        perguntas = db.execute("SELECT * FROM perguntas WHERE secao_id = ?", (secao_id,)).fetchall()
        for p in perguntas:
            db.execute(
                "INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, grid_rows, ordem, condicional, condicao_pergunta, condicao_valor) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (nova_secao_id, p['codigo'], p['texto'], p['tipo'], p['obrigatoria'], p['opcoes'], p['grid_rows'], p['ordem'], p['condicional'], p['condicao_pergunta'], p['condicao_valor'])
            )

        db.commit()
        flash('Seção duplicada com sucesso!', 'success')
        return redirect(url_for('admin_formulario_estrutura', formulario_id=secao['formulario_id']))

    @app.route('/admin/formulario/pergunta/nova/<int:formulario_id>', methods=['GET', 'POST'])
    @login_required
    def admin_pergunta_nova(formulario_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        secoes = db.execute(
            "SELECT * FROM secoes WHERE formulario_id = ? AND ativo = 1 ORDER BY ordem",
            (formulario_id,)
        ).fetchall()

        if request.method == 'POST':
            secao_id = request.form.get('secao_id', type=int)
            codigo = request.form.get('codigo', '').strip()
            texto = request.form.get('texto', '').strip()
            tipo = request.form.get('tipo', 'escala')
            obrigatoria = 1 if request.form.get('obrigatoria') else 0
            opcoes = request.form.get('opcoes', '').strip()
            grid_rows = request.form.get('grid_rows', '').strip()
            ordem = request.form.get('ordem', 0, type=int)

            if not secao_id or not texto:
                flash('Seção e texto são obrigatórios.', 'danger')
                return redirect(url_for('admin_pergunta_nova', formulario_id=formulario_id))

            db.execute(
                """INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, grid_rows, ordem)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (secao_id, codigo, texto, tipo, obrigatoria, opcoes if opcoes else None, grid_rows if grid_rows else None, ordem)
            )
            db.commit()
            flash('Pergunta criada com sucesso!', 'success')
            return redirect(url_for('admin_formulario_estrutura', formulario_id=formulario_id))

        secao_id = request.args.get('secao_id', type=int)
        max_ordem = db.execute("SELECT COALESCE(MAX(ordem), 0) as m FROM perguntas WHERE secao_id = ?", (secao_id,)).fetchone()['m'] if secao_id else 0
        return render_template('admin_pergunta_form.html', pergunta=None, secoes=secoes, secao_id=secao_id, max_ordem=max_ordem, formulario_id=formulario_id)

    @app.route('/admin/formulario/pergunta/<int:pergunta_id>/editar', methods=['GET', 'POST'])
    @login_required
    def admin_pergunta_editar(pergunta_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        pergunta = db.execute("SELECT * FROM perguntas WHERE id = ?", (pergunta_id,)).fetchone()
        if not pergunta:
            flash('Pergunta não encontrada.', 'danger')
            return redirect(url_for('admin_formularios'))

        secao = db.execute("SELECT formulario_id FROM secoes WHERE id = ?", (pergunta['secao_id'],)).fetchone()
        formulario_id = secao['formulario_id'] if secao else 1

        secoes = db.execute(
            "SELECT * FROM secoes WHERE formulario_id = ? AND ativo = 1 ORDER BY ordem",
            (formulario_id,)
        ).fetchall()

        if request.method == 'POST':
            secao_id = request.form.get('secao_id', type=int)
            codigo = request.form.get('codigo', '').strip()
            texto = request.form.get('texto', '').strip()
            tipo = request.form.get('tipo', 'escala')
            obrigatoria = 1 if request.form.get('obrigatoria') else 0
            opcoes = request.form.get('opcoes', '').strip()
            grid_rows = request.form.get('grid_rows', '').strip()
            ordem = request.form.get('ordem', 0, type=int)

            if not secao_id or not texto:
                flash('Seção e texto são obrigatórios.', 'danger')
                return redirect(url_for('admin_pergunta_editar', pergunta_id=pergunta_id))

            db.execute(
                """UPDATE perguntas SET secao_id = ?, codigo = ?, texto = ?, tipo = ?, obrigatoria = ?,
                   opcoes = ?, grid_rows = ?, ordem = ? WHERE id = ?""",
                (secao_id, codigo, texto, tipo, obrigatoria, opcoes if opcoes else None, grid_rows if grid_rows else None, ordem, pergunta_id)
            )
            db.commit()
            flash('Pergunta atualizada com sucesso!', 'success')
            return redirect(url_for('admin_formulario_estrutura', formulario_id=formulario_id))

        return render_template('admin_pergunta_form.html', pergunta=pergunta, secoes=secoes, secao_id=pergunta['secao_id'], max_ordem=0, formulario_id=formulario_id)

    @app.route('/admin/formulario/pergunta/<int:pergunta_id>/excluir', methods=['POST'])
    @login_required
    def admin_pergunta_excluir(pergunta_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        pergunta = db.execute("SELECT secao_id FROM perguntas WHERE id = ?", (pergunta_id,)).fetchone()
        secao = db.execute("SELECT formulario_id FROM secoes WHERE id = ?", (pergunta['secao_id'],)).fetchone()
        db.execute("UPDATE perguntas SET ativo = 0 WHERE id = ?", (pergunta_id,))
        db.commit()
        flash('Pergunta excluída com sucesso!', 'success')
        return redirect(url_for('admin_formulario_estrutura', formulario_id=secao['formulario_id']))

    @app.route('/admin/formulario/pergunta/<int:pergunta_id>/duplicar', methods=['POST'])
    @login_required
    def admin_pergunta_duplicar(pergunta_id):
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        pergunta = db.execute("SELECT * FROM perguntas WHERE id = ?", (pergunta_id,)).fetchone()
        if not pergunta:
            flash('Pergunta não encontrada.', 'danger')
            return redirect(url_for('admin_formularios'))

        secao = db.execute("SELECT formulario_id FROM secoes WHERE id = ?", (pergunta['secao_id'],)).fetchone()
        formulario_id = secao['formulario_id'] if secao else 1

        max_ordem = db.execute(
            "SELECT COALESCE(MAX(ordem), 0) as m FROM perguntas WHERE secao_id = ?",
            (pergunta['secao_id'],)
        ).fetchone()['m']

        db.execute(
            """INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, grid_rows, ordem, condicional, condicao_pergunta, condicao_valor)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (pergunta['secao_id'], pergunta['codigo'] + '_copia', pergunta['texto'], pergunta['tipo'],
             pergunta['obrigatoria'], pergunta['opcoes'], pergunta['grid_rows'], max_ordem + 1,
             pergunta['condicional'], pergunta['condicao_pergunta'], pergunta['condicao_valor'])
        )
        db.commit()
        flash('Pergunta duplicada com sucesso!', 'success')
        return redirect(url_for('admin_formulario_estrutura', formulario_id=formulario_id))
