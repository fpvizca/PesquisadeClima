from flask import render_template, request, redirect, session, url_for, flash
from auth import login_required, has_role, hash_senha
from db import get_db

def init_routes(app):

    @app.route('/admin/trocar-senha', methods=['GET', 'POST'])
    @login_required
    def admin_trocar_senha():
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        db = get_db()
        usuario = db.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],)).fetchone()

        if request.method == 'POST':
            senha_atual = request.form.get('senha_atual', '').strip()
            nova_senha = request.form.get('nova_senha', '').strip()
            confirmar_senha = request.form.get('confirmar_senha', '').strip()

            if not senha_atual or not nova_senha or not confirmar_senha:
                flash('Preencha todos os campos.', 'danger')
                return redirect(url_for('admin_trocar_senha'))

            if hash_senha(senha_atual) != usuario['senha_hash']:
                flash('Senha atual incorreta.', 'danger')
                return redirect(url_for('admin_trocar_senha'))

            if nova_senha != confirmar_senha:
                flash('As senhas não conferem.', 'danger')
                return redirect(url_for('admin_trocar_senha'))

            if len(nova_senha) < 6:
                flash('A nova senha deve ter no mínimo 6 caracteres.', 'danger')
                return redirect(url_for('admin_trocar_senha'))

            db.execute(
                "UPDATE usuarios SET senha_hash = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (hash_senha(nova_senha), session['usuario_id'])
            )
            db.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('admin_trocar_senha.html')

    @app.route('/admin/bloqueados', methods=['GET', 'POST'])
    @login_required
    def admin_bloqueados():
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('dashboard'))

        db = get_db()

        if request.method == 'POST':
            acao = request.form.get('acao')
            if acao == 'adicionar':
                novos = [l.strip().lower() for l in request.form.get('logins', '').replace(',', '\n').splitlines()]
                novos = [l for l in novos if l]
                if not novos:
                    flash('Informe ao menos um login.', 'warning')
                else:
                    for l in novos:
                        db.execute(
                            "INSERT OR IGNORE INTO usuarios_bloqueados (login, motivo) VALUES (?, ?)",
                            (l, request.form.get('motivo', '').strip() or 'Bloqueado pela administração')
                        )
                    db.commit()
                    flash(f'{len(novos)} login(s) bloqueado(s).', 'success')
            elif acao == 'remover':
                login = request.form.get('login', '')
                db.execute("DELETE FROM usuarios_bloqueados WHERE lower(login) = lower(?)", (login,))
                db.commit()
                flash(f'Login "{login}" desbloqueado.', 'success')
            return redirect(url_for('admin_bloqueados'))

        bloqueados = db.execute("SELECT * FROM usuarios_bloqueados ORDER BY login").fetchall()
        return render_template('admin_bloqueados.html', bloqueados=bloqueados)
