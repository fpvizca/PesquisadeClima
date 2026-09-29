"""CRUD do formulario e, principalmente, a numeracao das perguntas (Q1..Qn).

Regressao: criar/editar/duplicar perguntas nao renumeravam, e a pergunta nova
aparecia na pesquisa com o badge de codigo vazio.
"""
import re
import unittest

from tests.base import BaseTeste


ORDEM_AUTORITATIVA = (
    "SELECT p.id, p.codigo, p.texto FROM perguntas p "
    "JOIN secoes s ON s.id = p.secao_id "
    "WHERE p.ativo = 1 AND s.ativo = 1 AND s.formulario_id = ? "
    "ORDER BY s.ordem, p.ordem, p.id"
)


class TestFormulario(BaseTeste):

    def setUp(self):
        super().setUp()
        self.formulario = self._formulario_padrao()
        self.secao = self._sql(
            'SELECT * FROM secoes WHERE formulario_id = ? AND ativo = 1 ORDER BY ordem LIMIT 1',
            (self.formulario['id'],)
        )[0]
        self.criados = []

    def tearDown(self):
        for pid in self.criados:
            self._executar('DELETE FROM respostas WHERE pergunta_id = ?', (pid,))
            self._executar('DELETE FROM perguntas WHERE id = ?', (pid,))

    # helpers
    def _codigos(self):
        return [r['codigo'] for r in self._sql(ORDEM_AUTORITATIVA, (self.formulario['id'],))]

    def _criar_pergunta(self, texto):
        self.admin.post(f'/admin/formulario/pergunta/nova/{self.formulario["id"]}',
                        data={'texto': texto, 'tipo': 'escala', 'secao_id': str(self.secao['id']),
                              'descricao': 'descricao de teste', 'ordem': '999'},
                        follow_redirects=True)
        p = self._sql('SELECT * FROM perguntas WHERE texto = ? ORDER BY id DESC', (texto,))[0]
        self.criados.append(p['id'])
        return p

    # testes
    def test_criar_pergunta_ganha_codigo_sequencial(self):
        p = self._criar_pergunta('Pergunta Numerada')
        codigos = self._codigos()
        self.assertRegex(p['codigo'], r'^Q\d+$', f'codigo invalido: {p["codigo"]!r}')
        self.assertEqual(codigos, [f'Q{i+1}' for i in range(len(codigos))])

    def test_criar_pergunta_preserva_descricao(self):
        p = self._criar_pergunta('Pergunta Com Descricao')
        self.assertEqual(p['descricao'], 'descricao de teste')

    def test_duplicar_pergunta_gera_codigo_proprio(self):
        original = self._criar_pergunta('Pergunta Para Duplicar')
        self.admin.post(f'/admin/formulario/pergunta/{original["id"]}/duplicar', follow_redirects=True)
        duplicatas = [p for p in self._sql('SELECT * FROM perguntas WHERE texto = ?', ('Pergunta Para Duplicar',))
                      if p['id'] != original['id']]
        self.assertEqual(len(duplicatas), 1)
        d = duplicatas[0]
        self.criados.append(d['id'])

        self.assertNotEqual(d['codigo'], original['codigo'], 'duplicata reusou o codigo da original')
        self.assertNotIn('_copia', d['codigo'], f'codigo literal _copia no banco: {d["codigo"]!r}')
        codigos = self._codigos()
        self.assertEqual(codigos, [f'Q{i+1}' for i in range(len(codigos))])

    def test_excluir_e_soft_delete(self):
        p = self._criar_pergunta('Pergunta Para Excluir')
        self.admin.post(f'/admin/formulario/pergunta/{p["id"]}/excluir', follow_redirects=True)
        linha = self._sql('SELECT ativo FROM perguntas WHERE id = ?', (p['id'],))[0]
        self.assertEqual(linha['ativo'], 0, 'exclusao apagou a linha e quebrou o historico')
        visiveis = [r['id'] for r in self._sql(ORDEM_AUTORITATIVA, (self.formulario['id'],))]
        self.assertNotIn(p['id'], visiveis, 'pergunta excluida ainda aparece no formulario')
        codigos = self._codigos()
        self.assertEqual(codigos, [f'Q{i+1}' for i in range(len(codigos))])

    def test_duplicar_secao_copia_perguntas_com_codigos_proprios(self):
        antes = len(self._codigos())
        self.admin.post(f'/admin/formulario/secao/{self.secao["id"]}/duplicar', follow_redirects=True)
        copia = self._sql('SELECT * FROM secoes WHERE nome = ?', (self.secao['nome'] + ' (Cópia)',))[0]
        self.addCleanup(self._remover_secao, copia['id'])

        codigos_copia = [r['codigo'] for r in
                         self._sql('SELECT codigo FROM perguntas WHERE secao_id = ? AND ativo = 1', (copia['id'],))]
        self.assertTrue(codigos_copia, 'copia ficou sem perguntas')
        for cod in codigos_copia:
            self.assertRegex(cod, r'^Q\d+$', f'codigo invalido na copia: {cod!r}')

        codigos = self._codigos()
        self.assertEqual(len(codigos), antes + len(codigos_copia))
        self.assertEqual(len(codigos), len(set(codigos)), 'ha codigo repetido apos duplicar a secao')
        self.assertEqual(codigos, [f'Q{i+1}' for i in range(len(codigos))])

    def test_editar_pergunta_renumera(self):
        p = self._criar_pergunta('Pergunta Editavel')
        self.admin.post(f'/admin/formulario/pergunta/{p["id"]}/editar',
                        data={'texto': 'Pergunta Editada', 'tipo': 'escala',
                              'secao_id': str(self.secao['id']), 'ordem': str(p['ordem'])},
                        follow_redirects=True)
        codigos = self._codigos()
        self.assertEqual(codigos, [f'Q{i+1}' for i in range(len(codigos))])

    def test_pesquisa_nunca_mostra_codigo_vazio(self):
        self._criar_pergunta('Pergunta Visivel')
        self._garantir_ciclo_ativo()
        cid = self._ciclo_ativo()[0]['id']
        encontradas = 0
        for secao in self._sql('SELECT id FROM secoes WHERE formulario_id = ? AND ativo = 1 ORDER BY ordem',
                               (self.formulario['id'],)):
            html = self.colaborador.get(f'/pesquisa/secao/{secao["id"]}').get_data(as_text=True)
            for badge in re.findall(r'class="badge bg-secondary me-1">(.*?)</span>', html):
                encontradas += 1
                self.assertRegex(badge, r'^Q\d+$', f'badge invalido na secao {secao["id"]}: {badge!r}')
        self.assertGreater(encontradas, 0, 'nenhum badge verificado')

    def _remover_secao(self, secao_id):
        self._executar('DELETE FROM perguntas WHERE secao_id = ?', (secao_id,))
        self._executar('DELETE FROM secoes WHERE id = ?', (secao_id,))


if __name__ == '__main__':
    unittest.main()
