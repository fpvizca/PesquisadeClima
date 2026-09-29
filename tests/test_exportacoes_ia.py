"""Exportacoes, pagina de analise e integracao com o Ollama."""
import io
import json
import time
import unittest
import zipfile
from unittest import mock

from tests.base import BaseTeste


class TestPaginaAnalise(BaseTeste):
    """Regressao: a pagina quebrava (500) quando existia qualquer comentario,
    porque sqlite3.Row nao e serializavel em tojson."""

    def setUp(self):
        super().setUp()
        self._garantir_ciclo_ativo()
        self.ciclo_id = self._ciclo_ativo()[0]['id']
        # a primeira secao do formulario (Perfil) nao tem pergunta do tipo
        # escala, entao procuramos a primeira secao que realmente tenha uma
        self.pergunta = self._sql(
            "SELECT p.* FROM perguntas p JOIN secoes s ON s.id = p.secao_id"
            " WHERE p.ativo = 1 AND s.ativo = 1 AND p.tipo = 'escala'"
            ' ORDER BY s.ordem, p.id LIMIT 1'
        )[0]
        self._executar('DELETE FROM respostas WHERE ciclo_id = ?', (self.ciclo_id,))

    def tearDown(self):
        self._executar('DELETE FROM respostas WHERE ciclo_id = ?', (self.ciclo_id,))

    def _responder(self, comentario=None, valor=None):
        self._executar(
            'INSERT INTO respostas (ciclo_id, pergunta_id, usuario_id, valor, comentario) VALUES (?,?,?,?,?)',
            (self.ciclo_id, self.pergunta['id'], self.colaborador_id, valor, comentario)
        )

    def test_pagina_abre_sem_comentarios(self):
        self._responder(valor='Concordo')
        self.assertEqual(self.admin.get('/admin/analise').status_code, 200)

    def test_pagina_abre_com_comentarios(self):
        self._responder(valor='Concordo', comentario='Comentário do colaborador')
        r = self.admin.get('/admin/analise')
        self.assertEqual(r.status_code, 200, 'pagina de analise quebrou com comentario')
        html = r.get_data(as_text=True)
        # o comentario viaja no payload JSON do JS, com acentos escapados
        esperado = json.dumps('Comentário do colaborador', ensure_ascii=True)[1:-1]
        self.assertIn(esperado, html)
        self.assertIn('const comentarios', html)

    def test_pagina_abre_com_respostas_abertas(self):
        aberta = self._sql(
            "SELECT * FROM perguntas WHERE tipo IN ('texto','paragrafo') AND ativo = 1 LIMIT 1"
        )
        if not aberta:
            self.skipTest('formulario sem pergunta aberta')
        self._executar('INSERT INTO respostas (ciclo_id, pergunta_id, usuario_id, valor) VALUES (?,?,?,?)',
                       (self.ciclo_id, aberta[0]['id'], self.colaborador_id, 'Minha resposta aberta'))
        self.assertEqual(self.admin.get('/admin/analise').status_code, 200)

    def test_js_da_analise_por_pergunta_envia_comentarios(self):
        self._responder(valor='Concordo', comentario='Comentário relevante')
        html = self.admin.get('/admin/analise').get_data(as_text=True)
        self.assertIn('comentarios.filter(r => r.codigo === codigo)', html)
        self.assertIn('respostas_abertas: abertasPergunta, comentarios: comentsPergunta', html)


class TestApiAnaliseIa(BaseTeste):

    def setUp(self):
        super().setUp()
        self.payload = {
            'secao': 'Pergunta Q1',
            'dados': {
                'media': 4.0, 'total': 10, 'pct_satisfatorio': 70.0,
                'distribuicao': {'Concordo': 7, 'Discordo': 3},
                'texto_pergunta': 'A comunicação é clara?',
                'respostas_abertas': [{'codigo': 'Q1', 'texto': 'Resposta aberta'}],
                'comentarios': [{'codigo': 'Q1', 'comentario': 'Comentário do colaborador'}],
            }
        }

    def test_prompt_recebe_comentarios_e_respostas_abertas(self):
        import ollama_helper
        with mock.patch.object(ollama_helper, 'generate', return_value='analise') as m:
            r = self.admin.post('/api/analise-ia', json=self.payload)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json().get('response'), 'analise')
        prompt = m.call_args[0][0]
        self.assertIn('Comentário do colaborador', prompt)
        self.assertIn('Resposta aberta', prompt)
        self.assertIn('A comunicação é clara?', prompt)

    def test_analise_geral_recebe_texto_livre(self):
        import ollama_helper
        payload = {'secao': 'Geral', 'dados': {'media': 3.8, 'total': 10,
                                              'distribuicao': {'Concordo': 7},
                                              'respostas_abertas': [{'codigo': 'Q70', 'texto': 'aberta geral'}],
                                              'comentarios': [{'codigo': 'Q10', 'comentario': 'comentario geral'}]}}
        with mock.patch.object(ollama_helper, 'generate', return_value='analise') as m:
            self.admin.post('/api/analise-ia', json=payload)
        prompt = m.call_args[0][0]
        self.assertIn('aberta geral', prompt)
        self.assertIn('comentario geral', prompt)

    def test_colaborador_nao_usa_a_api(self):
        r = self.colaborador.post('/api/analise-ia', json=self.payload, follow_redirects=False)
        self.assertIn(r.status_code, (302, 403))

    def test_sem_ollama_degrada_sem_erro_500(self):
        import ollama_helper
        original = ollama_helper.OLLAMA_BASE
        ollama_helper.OLLAMA_BASE = 'http://127.0.0.1:9'
        ollama_helper.limpar_cache()
        try:
            r = self.admin.post('/api/analise-ia', json=self.payload)
            self.assertEqual(r.status_code, 200)
            msg = json.dumps(r.get_json(), ensure_ascii=False)
            self.assertIn('Erro', msg)
        finally:
            ollama_helper.OLLAMA_BASE = original
            ollama_helper.limpar_cache()


class TestOllamaHelper(unittest.TestCase):
    """Timeout, cache e circuit breaker do ollama_helper."""

    def setUp(self):
        import ollama_helper
        self.h = ollama_helper
        self.h.limpar_cache()
        self.orig_timeout = self.h.TIMEOUT

    def tearDown(self):
        self.h.limpar_cache()
        self.h.TIMEOUT = self.orig_timeout

    def _resposta_fake(self, texto='gerado'):
        class Resp:
            def read(self):
                return json.dumps({'response': texto}).encode('utf-8')

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False
        return Resp()

    def test_timeout_padrao_e_curto(self):
        self.assertLessEqual(self.h.TIMEOUT, 30, 'timeout alto demais: export Word faz ~90 chamadas')

    def test_cache_evita_segunda_chamada(self):
        with mock.patch.object(self.h.urllib.request, 'urlopen', return_value=self._resposta_fake()) as m:
            a = self.h.generate('prompt unico de teste')
            b = self.h.generate('prompt unico de teste')
        self.assertEqual(a, 'gerado')
        self.assertEqual(b, 'gerado')
        self.assertEqual(m.call_count, 1, 'cache nao evitou a segunda chamada')

    def test_prompts_diferentes_nao_compartilham_cache(self):
        with mock.patch.object(self.h.urllib.request, 'urlopen', return_value=self._resposta_fake()) as m:
            self.h.generate('prompt A')
            self.h.generate('prompt B')
        self.assertEqual(m.call_count, 2)

    def test_circuit_breaker_para_de_chamar_quando_falha(self):
        erro = OSError('conexao recusada')
        with mock.patch.object(self.h.urllib.request, 'urlopen', side_effect=erro) as m:
            primeira = self.h.generate('p1')
            segunda = self.h.generate('p2')
            terceira = self.h.generate('p3')
        self.assertIn('Erro', primeira)
        self.assertEqual(m.call_count, 1, 'continuou tentando rede durante o cooldown')
        self.assertEqual(segunda, primeira)
        self.assertEqual(terceira, primeira)

    def test_sucesso_zera_o_breaker(self):
        erro = OSError('conexao recusada')
        with mock.patch.object(self.h.urllib.request, 'urlopen', side_effect=erro):
            self.h.generate('p1')
        self.assertTrue(self.h.indisponivel(), 'breaker nao abriu apos a falha')

        # cooldown expirou: a proxima chamada volta a sair para a rede e,
        # tendo sucesso, deve fechar o breaker
        self.h._indisponivel_ate = 0
        with mock.patch.object(self.h.urllib.request, 'urlopen', return_value=self._resposta_fake()) as m:
            self.assertEqual(self.h.generate('p1'), 'gerado')
        self.assertEqual(m.call_count, 1)
        self.assertFalse(self.h.indisponivel(), 'sucesso nao fechou o breaker')


class TestExportacoes(BaseTeste):

    def setUp(self):
        super().setUp()
        self._garantir_ciclo_ativo()

    def test_exporta_excel(self):
        r = self.admin.get('/admin/exportar-excel')
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.get_data()), 3000)

    def test_exporta_word(self):
        r = self.admin.get('/admin/exportar-word')
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.get_data()), 3000)

    def _texto_word(self, dados):
        """O .docx e um zip: o texto so aparece depois de extrair document.xml."""
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            return z.read('word/document.xml').decode('utf-8')

    def test_exportacao_avisa_analises_omitidas_pelo_teto_de_ia(self):
        import ollama_helper
        with mock.patch.dict('os.environ', {'EXPORTAR_WORD_IA_MAX': '1'}):
            with mock.patch.object(ollama_helper, 'generate', return_value='analise') as m:
                r = self.admin.get('/admin/exportar-word')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(m.call_count, 1, 'o teto de IA nao foi respeitado')
        # com o teto em 1, o documento deve avisar que outras analises ficaram de fora
        texto = self._texto_word(r.get_data())
        self.assertIn('Nota:', texto)
        self.assertIn('EXPORTAR_WORD_IA_MAX', texto)

    def test_ia_desligada_nao_quebra_a_exportacao(self):
        with mock.patch.dict('os.environ', {'EXPORTAR_WORD_IA': '0'}):
            r = self.admin.get('/admin/exportar-word')
        self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    unittest.main()
