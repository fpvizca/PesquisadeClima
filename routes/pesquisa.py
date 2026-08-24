import json
import statistics
from flask import render_template, request, redirect, session, url_for, flash, jsonify
from auth import login_required, has_role
from db import get_db
import ollama_helper

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

        ja_respondeu = db.execute(
            "SELECT COUNT(*) as c FROM respostas WHERE ciclo_id = ? AND usuario_id = ?",
            (ciclo['id'], usuario_id)
        ).fetchone()['c']

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
            "SELECT * FROM perguntas WHERE secao_id = ? ORDER BY ordem",
            (secao_id,)
        ).fetchall()

        respostas_existentes = {}
        for p in perguntas:
            r = db.execute(
                "SELECT valor, comentario FROM respostas WHERE ciclo_id = ? AND usuario_id = ? AND pergunta_id = ?",
                (ciclo['id'], usuario_id, p['id'])
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
                        INSERT INTO respostas (ciclo_id, usuario_id, pergunta_id, valor, comentario)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(ciclo_id, usuario_id, pergunta_id)
                        DO UPDATE SET valor = excluded.valor, comentario = excluded.comentario, respondido_em = CURRENT_TIMESTAMP
                    """, (ciclo['id'], usuario_id, p['id'], valor if valor else None, comentario if comentario else None))
            db.commit()

            proximo_index = secao_index + 1
            if proximo_index < len(secoes):
                return redirect(url_for('pesquisa_secao', secao_id=secoes[proximo_index]['id']))
            else:
                flash('Pesquisa respondida com sucesso!', 'success')
                return redirect(url_for('minhas_respostas'))

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

        secoes = db.execute("SELECT * FROM secoes WHERE ativo = 1 ORDER BY ordem").fetchall()
        dados = []
        for secao in secoes:
            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? ORDER BY ordem",
                (secao['id'],)
            ).fetchall()
            perguntas_com_resposta = []
            for p in perguntas:
                r = db.execute(
                    "SELECT valor, comentario FROM respostas WHERE ciclo_id = ? AND usuario_id = ? AND pergunta_id = ?",
                    (ciclo['id'], usuario_id, p['id'])
                ).fetchone()
                perguntas_com_resposta.append({
                    'pergunta': p,
                    'valor': r['valor'] if r else None,
                    'comentario': r['comentario'] if r else None
                })
            dados.append({'secao': secao, 'perguntas': perguntas_com_resposta})

        return render_template('minhas_respostas.html',
            ciclo=ciclo,
            dados=dados
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
                "SELECT * FROM perguntas WHERE secao_id = ? ORDER BY ordem",
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

        total_respondentes = db.execute(
            "SELECT COUNT(DISTINCT usuario_id) as c FROM respostas WHERE ciclo_id = ?",
            (ciclo['id'],)
        ).fetchone()['c']

        return render_template('admin_resultados.html',
            ciclo=ciclo,
            dados=dados,
            total_respondentes=total_respondentes
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
        total_respondentes = db.execute(
            "SELECT COUNT(DISTINCT usuario_id) as c FROM respostas WHERE ciclo_id = ?",
            (ciclo['id'],)
        ).fetchone()['c']

        dados_secoes = []
        for secao in secoes:
            perguntas = db.execute(
                "SELECT * FROM perguntas WHERE secao_id = ? AND tipo = 'escala' ORDER BY ordem",
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
            total_respondentes=total_respondentes,
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
