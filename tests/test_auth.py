"""Autenticacao, bloqueios e controle de acesso."""
import unittest

from tests.base import BaseTeste


LOGINS_BLOQUEADOS = [
    'anderson.oliveira', 'camila.macedo', 'fernando.silva', 'gabriel.melo',
    'isabelly.silva', 'jailson.santos', 'julia.santos', 'lucca.seixas',
    'luciana.kurimori', 'marianne.vieira', 'samira.diniz',
]


class TestLogin(BaseTeste):

    def test_admin_entra(self):
        html = self.admin.get('/dashboard').get_data(as_text=True)
        self.assertIn('logout', html)

    def test_logout_encerra_sessao(self):
        self.admin.get('/logout', follow_redirects=True)
        r = self.admin.get('/admin/resultados', follow_redirects=False)
        self.assertEqual(r.status_code, 302)

    def test_senha_errada_nao_autentica(self):
        c = self._login('admin', 'senha-errada')
        self.assertNotIn('logout', c.get('/dashboard').get_data(as_text=True))

    def test_login_bloqueado_e_recusado(self):
        for login in LOGINS_BLOQUEADOS:
            with self.subTest(login=login):
                c = self._login(login, 'qualquer')
                r = c.post('/login', data={'login': login, 'senha': 'x'}, follow_redirects=True)
                self.assertNotIn('logout', r.get_data(as_text=True))

    def test_bloqueio_ignora_caixa(self):
        r = self._login('SAMIRA.DINIZ', 'x')
        self.assertNotIn('logout', r.get('/dashboard').get_data(as_text=True))

    def test_mensagem_de_bloqueio_explica_o_motivo(self):
        r = self._login('samira.diniz', 'x')
        html = r.post('/login', data={'login': 'samira.diniz', 'senha': 'x'},
                      follow_redirects=True).get_data(as_text=True)
        self.assertIn('VIZCA', html)
        self.assertIn('3 meses', html)

    def test_rota_admin_sem_sessao_redireciona(self):
        anon = self.app.test_client()
        r = anon.get('/admin/resultados', follow_redirects=False)
        self.assertEqual(r.status_code, 302)


class TestPermissoes(BaseTeste):

    ROTAS_ADMIN = [
        '/admin/resultados', '/admin/analise', '/admin/ciclos', '/admin/formularios',
        '/admin/bloqueados', '/admin/trocar-senha',
    ]

    def test_colaborador_nao_acessa_admin(self):
        for rota in self.ROTAS_ADMIN:
            with self.subTest(rota=rota):
                r = self.colaborador.get(rota, follow_redirects=False)
                self.assertIn(r.status_code, (302, 403))

    def test_colaborador_nao_anonimiza_ciclo(self):
        ciclos = self._sql('SELECT id FROM ciclos ORDER BY id LIMIT 1')
        if not ciclos:
            self.skipTest('sem ciclos no banco')
        r = self.colaborador.post(f'/admin/ciclos/{ciclos[0]["id"]}/anonimizar', follow_redirects=False)
        self.assertIn(r.status_code, (302, 403))

    def test_troca_de_senha_e_exclusiva_do_admin(self):
        r = self.colaborador.get('/admin/trocar-senha', follow_redirects=False)
        self.assertIn(r.status_code, (302, 403))


class TestTrocaDeSenha(BaseTeste):

    def test_rejeita_senha_atual_errada(self):
        r = self.admin.post('/admin/trocar-senha',
                            data={'senha_atual': 'errada', 'nova_senha': 'novasenha1', 'confirmar_senha': 'novasenha1'},
                            follow_redirects=True)
        self.assertIn('incorreta', r.get_data(as_text=True))

    def test_rejeita_senha_curta(self):
        r = self.admin.post('/admin/trocar-senha',
                            data={'senha_atual': 'admin123', 'nova_senha': 'abc', 'confirmar_senha': 'abc'},
                            follow_redirects=True)
        self.assertIn('mínimo 6', r.get_data(as_text=True))

    def test_rejeita_confirmacao_divergente(self):
        r = self.admin.post('/admin/trocar-senha',
                            data={'senha_atual': 'admin123', 'nova_senha': 'novasenha1', 'confirmar_senha': 'outra'},
                            follow_redirects=True)
        self.assertIn('não conferem', r.get_data(as_text=True))

    def test_altera_senha_e_invalida_a_antiga(self):
        r = self.admin.post('/admin/trocar-senha',
                            data={'senha_atual': 'admin123', 'nova_senha': 'novasenha1', 'confirmar_senha': 'novasenha1'},
                            follow_redirects=True)
        self.assertIn('alterada', r.get_data(as_text=True))

        self.assertIn('logout', self._login('admin', 'novasenha1').get('/dashboard').get_data(as_text=True))
        self.assertNotIn('logout', self._login('admin', 'admin123').get('/dashboard').get_data(as_text=True))

        # devolve a senha original para nao afetar outros testes
        self.admin.post('/admin/trocar-senha',
                        data={'senha_atual': 'novasenha1', 'nova_senha': 'admin123', 'confirmar_senha': 'admin123'},
                        follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
