"""Ciclos (criar/editar/ativar/excluir/anonimizar) e usuarios bloqueados."""
import unittest

from tests.base import BaseTeste


class TestCiclos(BaseTeste):

    def setUp(self):
        super().setUp()
        self.ciclo = self._criar_ciclo('Ciclo de Teste', 2030, ativo=1)

    def tearDown(self):
        self._executar('UPDATE ciclos SET ativo = 0 WHERE id = ?', (self.ciclo['id'],))
        self._executar('DELETE FROM ciclos WHERE nome LIKE ?', ('%de Teste',))

    def _criar_ciclo(self, nome, ano, ativo=0):
        dados = {'nome': nome, 'ano': str(ano), 'titulo': 'Título', 'texto_abertura': 'Abertura'}
        if ativo:
            dados['ativo'] = 'on'
        self.admin.post('/admin/ciclos/novo', data=dados, follow_redirects=True)
        return self._sql('SELECT * FROM ciclos WHERE nome = ?', (nome,))[0]

    def test_cria_com_titulo_e_abertura(self):
        c = self._criar_ciclo('Ciclo Completo', 2031)
        self.assertEqual(c['titulo'], 'Título')
        self.assertEqual(c['texto_abertura'], 'Abertura')

    def test_apenas_um_ciclo_ativo(self):
        segundo = self._criar_ciclo('Ciclo Ativo', 2032, ativo=1)
        ativos = [r['id'] for r in self._sql('SELECT id FROM ciclos WHERE ativo = 1')]
        self.assertEqual(ativos, [segundo['id']])
        self._executar('UPDATE ciclos SET ativo = 0 WHERE id = ?', (segundo['id'],))

    def test_edita_ciclo(self):
        self.admin.post(f'/admin/ciclos/{self.ciclo["id"]}/editar',
                        data={'nome': 'Ciclo Renomeado', 'ano': '2030'}, follow_redirects=True)
        self.assertEqual(self._sql('SELECT nome FROM ciclos WHERE id = ?', (self.ciclo['id'],))[0]['nome'],
                         'Ciclo Renomeado')

    def test_exclui_ciclo_vazio(self):
        self.admin.post(f'/admin/ciclos/{self.ciclo["id"]}/excluir', follow_redirects=True)
        self.assertEqual(self._sql('SELECT COUNT(*) AS n FROM ciclos WHERE id = ?', (self.ciclo['id'],))[0]['n'], 0)

    def test_anonimizar_preserva_respostas_e_remove_vinculo(self):
        self._garantir_ciclo_ativo()
        cid = self._ciclo_ativo()[0]['id']
        secao = self._sql('SELECT * FROM secoes WHERE ativo = 1 ORDER BY ordem LIMIT 1')[0]
        p = self._sql('SELECT * FROM perguntas WHERE secao_id = ? AND ativo = 1 LIMIT 1', (secao['id'],))[0]
        self._executar('INSERT INTO respostas (ciclo_id, pergunta_id, usuario_id, valor) VALUES (?,?,?,?)',
                       (cid, p['id'], self.colaborador_id, 'Concordo'))
        self._executar('UPDATE ciclos SET anonimizado_em = NULL WHERE id = ?', (cid,))

        antes = self._sql('SELECT COUNT(*) AS n FROM respostas WHERE ciclo_id = ?', (cid,))[0]['n']
        self.assertGreater(antes, 0)

        self.admin.post(f'/admin/ciclos/{cid}/anonimizar', follow_redirects=True)

        depois = self._sql('SELECT COUNT(*) AS n FROM respostas WHERE ciclo_id = ?', (cid,))[0]['n']
        vinculadas = self._sql('SELECT COUNT(*) AS n FROM respostas WHERE ciclo_id = ? AND usuario_id IS NOT NULL',
                               (cid,))[0]['n']
        marca = self._sql('SELECT anonimizado_em FROM ciclos WHERE id = ?', (cid,))[0]['anonimizado_em']

        self.assertEqual(depois, antes, 'anonimizar apagou respostas')
        self.assertEqual(vinculadas, 0, 'anonimizar deixou vinculo com colaborador')
        self.assertTrue(marca, 'ciclo nao foi marcado como anonimizado')

    def test_anonimizar_e_idempotente(self):
        self._garantir_ciclo_ativo()
        cid = self._ciclo_ativo()[0]['id']
        self._executar('UPDATE ciclos SET anonimizado_em = NULL WHERE id = ?', (cid,))
        self.admin.post(f'/admin/ciclos/{cid}/anonimizar', follow_redirects=True)
        marca = self._sql('SELECT anonimizado_em FROM ciclos WHERE id = ?', (cid,))[0]['anonimizado_em']
        r = self.admin.post(f'/admin/ciclos/{cid}/anonimizar', follow_redirects=True)
        self.assertIn('já foi anonimizado', r.get_data(as_text=True))
        self.assertEqual(self._sql('SELECT anonimizado_em FROM ciclos WHERE id = ?', (cid,))[0]['anonimizado_em'],
                         marca)


class TestBloqueados(BaseTeste):

    def test_adiciona_varios_de_uma_vez(self):
        self.admin.post('/admin/bloqueados',
                        data={'acao': 'adicionar', 'logins': 'a.teste\nb.teste, c.teste', 'motivo': 'teste'},
                        follow_redirects=True)
        n = self._sql('SELECT COUNT(*) AS n FROM usuarios_bloqueados WHERE login IN (?,?,?)',
                      ('a.teste', 'b.teste', 'c.teste'))[0]['n']
        self.assertEqual(n, 3)

    def test_remove_bloqueio(self):
        self.admin.post('/admin/bloqueados',
                        data={'acao': 'adicionar', 'logins': 'remover.teste', 'motivo': 'teste'},
                        follow_redirects=True)
        self.admin.post('/admin/bloqueados',
                        data={'acao': 'remover', 'login': 'remover.teste'}, follow_redirects=True)
        n = self._sql('SELECT COUNT(*) AS n FROM usuarios_bloqueados WHERE login = ?', ('remover.teste',))[0]['n']
        self.assertEqual(n, 0)

    def test_bloqueio_bloqueia_o_login(self):
        self.admin.post('/admin/bloqueados',
                        data={'acao': 'adicionar', 'logins': 'novo.bloqueio', 'motivo': 'teste'},
                        follow_redirects=True)
        try:
            c = self._login('novo.bloqueio', 'x')
            self.assertNotIn('logout', c.get('/dashboard').get_data(as_text=True))
        finally:
            self.admin.post('/admin/bloqueados', data={'acao': 'remover', 'login': 'novo.bloqueio'},
                            follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
