import json
import statistics
from flask import render_template, request, redirect, session, url_for, flash, jsonify
from auth import login_required, has_role
from db import get_db
import ollama_helper

from flask import make_response

def init_routes(app):

    @app.route('/pesquisa')
    @login_required
    def pesquisa():
        db = get_db()
        usuario_id = session['usuario_id']
        ciclo = db.execute("SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1").fetchone()
        if not ciclo:
            flash('Nenhum ciclo ativo encontrado.', 'warning')
            return redirect(url_for('index'))

        cookie_name = f'clima_respondeu_{ciclo["id"]}'
        ja_respondeu_cookie = request.cookies.get(cookie_name)

        ja_respondeu = db.execute(
            "SELECT COUNT(*) as c FROM respondentes WHERE ciclo_id = ? AND usuario_id = ?",
            (ciclo['id'], usuario_id)
        ).fetchone()['c'] or ja_respondeu_cookie

        secoes = db.execute("SELECT * FROM secoes WHERE ativo = 1 ORDER BY ordem").fetchall()
        total_perguntas = db.execute(
            "SELECT COUNT(*) as c FROM perguntas WHERE secao_id IN (SELECT id FROM secoes WHERE ativo = 1)"
        ).fetchone()['c']

        return render_template('pesquisa.html',
            ciclo=ciclo,
            ja_respondeu=ja_respondeu,
            secoes=secoes,
            total_perguntas=total_perguntas
        )

    @app.route('/pesquisa/secao/<int:secao_id>', methods=['GET', 'POST'])
    @login_required
    def pesquisa_secao(secao_id):
        db = get_db()
        usuario_id = session['usuario_id']
        ciclo = db.execute("SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1").fetchone()
        if not ciclo:
            flash('Nenhum ciclo ativo encontrado.', 'warning')
            return redirect(url_for('index'))

        secoes = db.execute("SELECT * FROM secoes WHERE ativo = 1 ORDER BY ordem").fetchall()
        secao_atual = None
        for i, s in enumerate(secoes):
            if s['id'] == secao_id:
                secao_atual = s
                secao_index = i
                break

        if not secao_atual:
            return redirect(url_for('pesquisa'))

        perguntas = db.execute(
            "SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 ORDER BY ordem",
            (secao_id,)
        ).fetchall()

        respostas_existentes = {}
        for p in perguntas:
            r = db.execute(
                "SELECT valor, comentario FROM respostas WHERE ciclo_id = ? AND pergunta_id = ?",
                (ciclo['id'], p['id'])
            ).fetchone()
            if r:
                respostas_existentes[p['id']] = {'valor': r['valor'], 'comentario': r['comentario']}

        if request.method == 'POST':
            for p in perguntas:
                valor = request.form.get(f'pergunta_{p["id"]}', '').strip()
                comentario = request.form.get(f'comentario_{p["id"]}', '').strip()

                if p['obrigatoria'] and not valor:
                    flash(f'Por favor, responda: {p["texto"]}', 'danger')
                    return redirect(url_for('pesquisa_secao', secao_id=secao_id))

                if valor or comentario:
                    db.execute("""
                        INSERT INTO respostas (ciclo_id, pergunta_id, valor, comentario)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(ciclo_id, pergunta_id)
                        DO UPDATE SET valor = excluded.valor, comentario = excluded.comentario, respondido_em = CURRENT_TIMESTAMP
                    """, (ciclo['id'], p['id'], valor if valor else None, comentario if comentario else None))
            db.commit()

            proximo_index = secao_index + 1
            if proximo_index < len(secoes):
                return redirect(url_for('pesquisa_secao', secao_id=secoes[proximo_index]['id']))
            else:
                db.execute(
                    "INSERT OR IGNORE INTO respondentes (ciclo_id, usuario_id) VALUES (?, ?)",
                    (ciclo['id'], usuario_id)
                )
                db.commit()
                flash('Pesquisa respondida com sucesso!', 'success')
                resp = make_response(redirect(url_for('minhas_respostas')))
                cookie_name = f'clima_respondeu_{ciclo["id"]}'
                resp.set_cookie(cookie_name, '1', max_age=60*60*24*365)
                return resp

        proxima_secao = secoes[secao_index + 1]['id'] if secao_index + 1 < len(secoes) else None

        return render_template('pesquisa_secao.html',
            ciclo=ciclo,
            secao=secao_atual,
            perguntas=perguntas,
            respostas_existentes=respostas_existentes,
            total_secoes=len(secoes),
            secao_atual_index=secao_index + 1,
            proxima_secao=proxima_secao,
            secoes=secoes
        )

    @app.route('/minhas-respostas')
    @login_required
    def minhas_respostas():
        db = get_db()
        usuario_id = session['usuario_id']
        ciclo = db.execute("SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1").fetchone()
        if not ciclo:
            flash('Nenhum ciclo ativo encontrado.', 'warning')
            return redirect(url_for('index'))

        cookie_name = f'clima_respondeu_{ciclo["id"]}'
        ja_respondeu_cookie = request.cookies.get(cookie_name)

        ja_respondeu = db.execute(
            "SELECT COUNT(*) as c FROM respondentes WHERE ciclo_id = ? AND usuario_id = ?",
            (ciclo['id'], usuario_id)
        ).fetchone()['c'] or ja_respondeu_cookie

        return render_template('minhas_respostas.html',
            ciclo=ciclo,
            ja_respondeu=ja_respondeu
        )

    @app.route('/admin/resultados')
    @login_required
    def admin_resultados():
        db = get_db()
        usuario_id = session['usuario_id']
        if not has_role(usuario_id, 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        ciclo = db.execute("SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1").fetchone()
        if not ciclo:
            flash('Nenhum ciclo ativo encontrado.', 'warning')
            return redirect(url_for('index'))

        secoes = db.execute("SELECT * FROM secoes WHERE ativo = 1 ORDER BY ordem").fetchall()
        dados = []
        for secao in secoes:
            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 ORDER BY ordem",
                (secao['id'],)
            ).fetchall()
            perguntas_com_stats = []
            for p in perguntas:
                if p['tipo'] == 'escala':
                    stats = db.execute("""
                        SELECT
                            COUNT(*) as total,
                            AVG(CASE WHEN valor = 'Concordo totalmente' THEN 5
                                     WHEN valor = 'Concordo' THEN 4
                                     WHEN valor = 'Não concordo e nem discordo' THEN 3
                                     WHEN valor = 'Discordo' THEN 2
                                     WHEN valor = 'Discordo totalmente' THEN 1
                                     ELSE NULL END) as media
                        FROM respostas WHERE ciclo_id = ? AND pergunta_id = ? AND valor IS NOT NULL
                    """, (ciclo['id'], p['id'])).fetchone()
                    perguntas_com_stats.append({
                        'pergunta': p,
                        'total': stats['total'],
                        'media': round(stats['media'], 2) if stats['media'] else None
                    })
                else:
                    respostas = db.execute(
                        "SELECT valor FROM respostas WHERE ciclo_id = ? AND pergunta_id = ? AND valor IS NOT NULL",
                        (ciclo['id'], p['id'])
                    ).fetchall()
                    perguntas_com_stats.append({
                        'pergunta': p,
                        'total': len(respostas),
                        'respostas': [r['valor'] for r in respostas]
                    })
            dados.append({'secao': secao, 'perguntas': perguntas_com_stats})

        total_habilitados = db.execute(
            "SELECT COUNT(*) as c FROM usuario_roles WHERE role = 'colaborador'"
        ).fetchone()['c']

        total_respostas = db.execute(
            "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ?",
            (ciclo['id'],)
        ).fetchone()['c']

        return render_template('admin_resultados.html',
            ciclo=ciclo,
            dados=dados,
            total_habilitados=total_habilitados,
            total_respostas=total_respostas
        )

    @app.route('/admin/analise')
    @login_required
    def admin_analise():
        db = get_db()
        usuario_id = session['usuario_id']
        if not has_role(usuario_id, 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        ciclo = db.execute("SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1").fetchone()
        if not ciclo:
            flash('Nenhum ciclo ativo encontrado.', 'warning')
            return redirect(url_for('index'))

        secoes = db.execute("SELECT * FROM secoes WHERE ativo = 1 ORDER BY ordem").fetchall()
        total_habilitados = db.execute(
            "SELECT COUNT(*) as c FROM usuario_roles WHERE role = 'colaborador'"
        ).fetchone()['c']

        total_respostas_db = db.execute(
            "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ?",
            (ciclo['id'],)
        ).fetchone()['c']

        dados_secoes = []
        for secao in secoes:
            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 AND tipo = 'escala' ORDER BY ordem",
                (secao['id'],)
            ).fetchall()

            medias = []
            distribuicao = {'Concordo totalmente': 0, 'Concordo': 0, 'Não concordo e nem discordo': 0, 'Discordo': 0, 'Discordo totalmente': 0}
            total_pond = 0
            total_respostas = 0

            perguntas_dados = []
            for p in perguntas:
                contagem = db.execute("""
                    SELECT valor, COUNT(*) as cnt FROM respostas
                    WHERE ciclo_id = ? AND pergunta_id = ? AND valor IS NOT NULL
                    GROUP BY valor
                """, (ciclo['id'], p['id'])).fetchall()

                mapa = {r['valor']: r['cnt'] for r in contagem}
                total_p = sum(mapa.values())

                if total_p > 0:
                    nota = (mapa.get('Concordo totalmente', 0) * 5 + mapa.get('Concordo', 0) * 4 +
                            mapa.get('Não concordo e nem discordo', 0) * 3 + mapa.get('Discordo', 0) * 2 +
                            mapa.get('Discordo totalmente', 0) * 1) / total_p
                    medias.append(nota)

                    pct_satisfatorio = ((mapa.get('Concordo totalmente', 0) + mapa.get('Concordo', 0)) / total_p * 100) if total_p > 0 else 0

                    for k in distribuicao:
                        distribuicao[k] += mapa.get(k, 0)
                    total_pond += total_p
                    total_respostas += total_p
                else:
                    nota = None
                    pct_satisfatorio = 0

                perguntas_dados.append({
                    'codigo': p['codigo'],
                    'texto': p['texto'],
                    'total': total_p,
                    'nota': round(nota, 2) if nota else None,
                    'pct_satisfatorio': round(pct_satisfatorio, 1),
                    'distribuicao': {k: mapa.get(k, 0) for k in ['Concordo totalmente', 'Concordo', 'Não concordo e nem discordo', 'Discordo', 'Discordo totalmente']}
                })

            media_secao = round(statistics.mean(medias), 2) if medias else None
            desvio = round(statistics.stdev(medias), 2) if len(medias) > 1 else 0
            pct_total_satisf = round((distribuicao['Concordo totalmente'] + distribuicao['Concordo']) / total_pond * 100, 1) if total_pond > 0 else 0

            dados_secoes.append({
                'secao': {'id': secao['id'], 'nome': secao['nome']},
                'media': media_secao,
                'desvio': desvio,
                'pct_satisfatorio': pct_total_satisf,
                'total_respostas': total_pond,
                'perguntas': perguntas_dados,
                'distribuicao': distribuicao
            })

        perguntas_abertas = db.execute("""
            SELECT p.codigo, p.texto, p.secao_id, s.nome as secao_nome, r.valor
            FROM respostas r JOIN perguntas p ON r.pergunta_id = p.id JOIN secoes s ON p.secao_id = s.id
            WHERE r.ciclo_id = ? AND p.tipo IN ('texto', 'paragrafo') AND r.valor IS NOT NULL AND r.valor != ''
            ORDER BY s.ordem, p.ordem
        """, (ciclo['id'],)).fetchall()

        return render_template('admin_analise.html',
            ciclo=ciclo,
            dados_secoes=dados_secoes,
            total_habilitados=total_habilitados,
            total_respostas=total_respostas_db,
            perguntas_abertas=perguntas_abertas
        )

    @app.route('/api/analise-ia', methods=['POST'])
    @login_required
    def api_analise_ia():
        if not has_role(session['usuario_id'], 'admin'):
            return jsonify({'error': 'Acesso negado'}), 403

        data = request.get_json()
        secao_nome = data.get('secao', 'Geral')
        dados = data.get('dados', {})

        prompt = f"""Gere uma análise profissional no estilo de relatório de pesquisa de clima organizacional para a seção "{secao_nome}".

Dados estatísticos:
- Média da seção: {dados.get('media', 'N/A')}
- Total de respostas: {dados.get('total', 'N/A')}
- % Satisfatório (Concordo + Concordo Totalmente): {dados.get('pct_satisfatorio', 'N/A')}%

Distribuição das respostas:
{json.dumps(dados.get('distribuicao', {}), ensure_ascii=False, indent=2)}

Perguntas com menores notas:
{json.dumps(dados.get('menores_notas', []), ensure_ascii=False, indent=2)}

Perguntas com maiores notas:
{json.dumps(dados.get('maiores_notas', []), ensure_ascii=False, indent=2)}

Respostas abertas relevantes:
{json.dumps(dados.get('respostas_abertas', []), ensure_ascii=False, indent=2)}

Escreva uma análise:
1. Resumo executivo da seção
2. Pontos fortes identificados
3. Pontos de atenção
4. Comparação com benchmarks (ideal > 4.0)
5. Recomendações de ações

Seja objetivo, use dados numéricos e escreva em português brasileiro profissional."""

        response = ollama_helper.generate(prompt)
        return jsonify({'response': response})

    @app.route('/admin/exportar-excel')
    @login_required
    def admin_exportar_excel():
        from flask import send_file
        import io
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        db = get_db()
        if not has_role(session['usuario_id'], 'admin'):
            flash('Acesso negado.', 'danger')
            return redirect(url_for('pesquisa'))

        ciclo = db.execute("SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id DESC LIMIT 1").fetchone()
        if not ciclo:
            flash('Nenhum ciclo ativo encontrado.', 'warning')
            return redirect(url_for('index'))

        wb = Workbook()

        # Estilos
        header_font = Font(name='Arial', bold=True, color='FFFFFF', size=11)
        header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        section_font = Font(name='Arial', bold=True, size=12, color='1F4E79')
        normal_font = Font(name='Arial', size=10)
        green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        yellow_fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
        red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        # Aba 1: Resumo por Seção
        ws_resumo = wb.active
        ws_resumo.title = 'Resumo'
        ws_resumo.column_dimensions['A'].width = 35
        ws_resumo.column_dimensions['B'].width = 15
        ws_resumo.column_dimensions['C'].width = 18
        ws_resumo.column_dimensions['D'].width = 20

        ws_resumo.merge_cells('A1:D1')
        ws_resumo['A1'] = ciclo['nome']
        ws_resumo['A1'].font = Font(name='Arial', bold=True, size=14, color='1F4E79')

        total_habilitados = db.execute(
            "SELECT COUNT(*) as c FROM usuario_roles WHERE role = 'colaborador'"
        ).fetchone()['c']

        total_respostas = db.execute(
            "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ?",
            (ciclo['id'],)
        ).fetchone()['c']

        ws_resumo['A2'] = f'Habilitados: {total_habilitados} | Respostas: {total_respostas}'
        ws_resumo['A2'].font = Font(name='Arial', size=10, italic=True)

        row = 4
        headers = ['Seção', 'Média', '% Satisfatório', 'Total Respostas']
        for col, h in enumerate(headers, 1):
            cell = ws_resumo.cell(row=row, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            cell.border = thin_border

        secoes = db.execute("SELECT * FROM secoes WHERE ativo = 1 ORDER BY ordem").fetchall()
        row = 5
        for secao in secoes:
            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 AND tipo = 'escala' ORDER BY ordem",
                (secao['id'],)
            ).fetchall()

            medias = []
            total_pond = 0
            total_satisf = 0

            for p in perguntas:
                contagem = db.execute("""
                    SELECT valor, COUNT(*) as cnt FROM respostas
                    WHERE ciclo_id = ? AND pergunta_id = ? AND valor IS NOT NULL
                    GROUP BY valor
                """, (ciclo['id'], p['id'])).fetchall()

                mapa = {r['valor']: r['cnt'] for r in contagem}
                total_p = sum(mapa.values())
                if total_p > 0:
                    nota = (mapa.get('Concordo totalmente', 0) * 5 + mapa.get('Concordo', 0) * 4 +
                            mapa.get('Não concordo e nem discordo', 0) * 3 + mapa.get('Discordo', 0) * 2 +
                            mapa.get('Discordo totalmente', 0) * 1) / total_p
                    medias.append(nota)
                    total_pond += total_p
                    total_satisf += mapa.get('Concordo totalmente', 0) + mapa.get('Concordo', 0)

            media = round(sum(medias) / len(medias), 2) if medias else None
            pct = round(total_satisf / total_pond * 100, 1) if total_pond > 0 else 0

            ws_resumo.cell(row=row, column=1, value=secao['nome']).font = normal_font
            ws_resumo.cell(row=row, column=1).border = thin_border

            cell_media = ws_resumo.cell(row=row, column=2, value=media)
            cell_media.font = normal_font
            cell_media.alignment = Alignment(horizontal='center')
            cell_media.border = thin_border
            if media:
                cell_media.fill = green_fill if media >= 4 else yellow_fill if media >= 3 else red_fill

            cell_pct = ws_resumo.cell(row=row, column=3, value=f'{pct}%')
            cell_pct.font = normal_font
            cell_pct.alignment = Alignment(horizontal='center')
            cell_pct.border = thin_border

            ws_resumo.cell(row=row, column=4, value=total_pond).font = normal_font
            ws_resumo.cell(row=row, column=4).alignment = Alignment(horizontal='center')
            ws_resumo.cell(row=row, column=4).border = thin_border

            row += 1

        # Aba 2: Detalhamento por Pergunta
        ws_detalhe = wb.create_sheet('Detalhamento')
        ws_detalhe.column_dimensions['A'].width = 10
        ws_detalhe.column_dimensions['B'].width = 60
        ws_detalhe.column_dimensions['C'].width = 12
        ws_detalhe.column_dimensions['D'].width = 12
        ws_detalhe.column_dimensions['E'].width = 12
        ws_detalhe.column_dimensions['F'].width = 12
        ws_detalhe.column_dimensions['G'].width = 12
        ws_detalhe.column_dimensions['H'].width = 12
        ws_detalhe.column_dimensions['I'].width = 12

        row = 1
        headers2 = ['Código', 'Pergunta', 'Total', 'Média', 'Conc. Totalmente', 'Concordo', 'Neutro', 'Discordo', 'Disc. Totalmente']
        for col, h in enumerate(headers2, 1):
            cell = ws_detalhe.cell(row=row, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', wrap_text=True)
            cell.border = thin_border

        row = 2
        for secao in secoes:
            ws_detalhe.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
            cell = ws_detalhe.cell(row=row, column=1, value=secao['nome'])
            cell.font = section_font
            row += 1

            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 ORDER BY ordem",
                (secao['id'],)
            ).fetchall()

            for p in perguntas:
                contagem = db.execute("""
                    SELECT valor, COUNT(*) as cnt FROM respostas
                    WHERE ciclo_id = ? AND pergunta_id = ? AND valor IS NOT NULL
                    GROUP BY valor
                """, (ciclo['id'], p['id'])).fetchall()

                mapa = {r['valor']: r['cnt'] for r in contagem}
                total_p = sum(mapa.values())

                if total_p > 0 and p['tipo'] == 'escala':
                    nota = (mapa.get('Concordo totalmente', 0) * 5 + mapa.get('Concordo', 0) * 4 +
                            mapa.get('Não concordo e nem discordo', 0) * 3 + mapa.get('Discordo', 0) * 2 +
                            mapa.get('Discordo totalmente', 0) * 1) / total_p
                    nota = round(nota, 2)
                else:
                    nota = None

                ws_detalhe.cell(row=row, column=1, value=p['codigo']).font = normal_font
                ws_detalhe.cell(row=row, column=1).border = thin_border
                ws_detalhe.cell(row=row, column=2, value=p['texto']).font = normal_font
                ws_detalhe.cell(row=row, column=2).border = thin_border
                ws_detalhe.cell(row=row, column=3, value=total_p).font = normal_font
                ws_detalhe.cell(row=row, column=3).alignment = Alignment(horizontal='center')
                ws_detalhe.cell(row=row, column=3).border = thin_border

                cell_nota = ws_detalhe.cell(row=row, column=4, value=nota)
                cell_nota.font = normal_font
                cell_nota.alignment = Alignment(horizontal='center')
                cell_nota.border = thin_border
                if nota:
                    cell_nota.fill = green_fill if nota >= 4 else yellow_fill if nota >= 3 else red_fill

                ws_detalhe.cell(row=row, column=5, value=mapa.get('Concordo totalmente', 0)).font = normal_font
                ws_detalhe.cell(row=row, column=5).alignment = Alignment(horizontal='center')
                ws_detalhe.cell(row=row, column=5).border = thin_border

                ws_detalhe.cell(row=row, column=6, value=mapa.get('Concordo', 0)).font = normal_font
                ws_detalhe.cell(row=row, column=6).alignment = Alignment(horizontal='center')
                ws_detalhe.cell(row=row, column=6).border = thin_border

                ws_detalhe.cell(row=row, column=7, value=mapa.get('Não concordo e nem discordo', 0)).font = normal_font
                ws_detalhe.cell(row=row, column=7).alignment = Alignment(horizontal='center')
                ws_detalhe.cell(row=row, column=7).border = thin_border

                ws_detalhe.cell(row=row, column=8, value=mapa.get('Discordo', 0)).font = normal_font
                ws_detalhe.cell(row=row, column=8).alignment = Alignment(horizontal='center')
                ws_detalhe.cell(row=row, column=8).border = thin_border

                ws_detalhe.cell(row=row, column=9, value=mapa.get('Discordo totalmente', 0)).font = normal_font
                ws_detalhe.cell(row=row, column=9).alignment = Alignment(horizontal='center')
                ws_detalhe.cell(row=row, column=9).border = thin_border

                row += 1

        # Aba 3: Respostas Abertas
        perguntas_abertas = db.execute("""
            SELECT p.codigo, p.texto, s.nome as secao_nome, r.valor
            FROM respostas r JOIN perguntas p ON r.pergunta_id = p.id JOIN secoes s ON p.secao_id = s.id
            WHERE r.ciclo_id = ? AND p.tipo IN ('texto', 'paragrafo') AND r.valor IS NOT NULL AND r.valor != ''
            ORDER BY s.ordem, p.ordem
        """, (ciclo['id'],)).fetchall()

        if perguntas_abertas:
            ws_abertas = wb.create_sheet('Respostas Abertas')
            ws_abertas.column_dimensions['A'].width = 10
            ws_abertas.column_dimensions['B'].width = 50
            ws_abertas.column_dimensions['C'].width = 30
            ws_abertas.column_dimensions['D'].width = 60

            row = 1
            headers3 = ['Código', 'Pergunta', 'Seção', 'Resposta']
            for col, h in enumerate(headers3, 1):
                cell = ws_abertas.cell(row=row, column=col, value=h)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center', wrap_text=True)
                cell.border = thin_border

            row = 2
            for r in perguntas_abertas:
                ws_abertas.cell(row=row, column=1, value=r['codigo']).font = normal_font
                ws_abertas.cell(row=row, column=1).border = thin_border
                ws_abertas.cell(row=row, column=2, value=r['texto']).font = normal_font
                ws_abertas.cell(row=row, column=2).border = thin_border
                ws_abertas.cell(row=row, column=3, value=r['secao_nome']).font = normal_font
                ws_abertas.cell(row=row, column=3).border = thin_border
                ws_abertas.cell(row=row, column=4, value=r['valor']).font = normal_font
                ws_abertas.cell(row=row, column=4).border = thin_border
                ws_abertas.cell(row=row, column=4).alignment = Alignment(wrap_text=True)
                row += 1

        # Salvar
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f'Resultados_Clima_{ciclo["ano"]}.xlsx'
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=filename)
