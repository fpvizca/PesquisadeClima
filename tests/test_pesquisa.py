"""Fluxo da pesquisa: responder, salvar parcial, reabrir e editar."""
import re
import unittest

from tests.base import BaseTeste, VALORES_ESCALA


class TestPesquisa(BaseTeste):

    def setUp(self):
        super().setUp()
        self._garantir_ciclo_ativo()
        self.secao = self._sql(
            "SELECT s.* FROM secoes s JOIN perguntas p ON p.secao_id = s.id "
            "WHERE p.tipo = 'escala' AND s.ativo = 1 GROUP BY s.id ORDER BY s.ordem"
        )[0]
        self.perguntas = self._sql(
            "SELECT * FROM perguntas WHERE secao_id = ? AND tipo = 'escala' AND ativo = 1 ORDER BY ordem",
            (self.secao['id'],)
        )
        # limpa respostas deste colaborador nas perguntas da secao
        for p in self.perguntas:
            self._executar('DELETE FROM respostas WHERE pergunta_id = ? AND usuario_id = ?',
                           (p['id'], self.colaborador_id))

    def test_pagina_abre(self):
        r = self.colaborador.get(f'/pesquisa/secao/{self.secao["id"]}')
        self.assertEqual(r.status_code, 200)

    def test_escala_renderiza_as_cinco_opcoes(self):
        html = self.colaborador.get(f'/pesquisa/secao/{self.secao["id"]}').get_data(as_text=True)
        for valor in VALORES_ESCALA:
            self.assertIn(f'value="{valor}"', html)

    def test_responde_e_salva(self):
        alvo = self.perguntas[0]
        self.colaborador.post(f'/pesquisa/secao/{self.secao["id"]}',
                              data={f'pergunta_{alvo["id"]}': 'Concordo', 'acao': 'salvar_parcial'},
                              follow_redirects=True)
        linhas = self._sql('SELECT valor FROM respostas WHERE pergunta_id = ? AND usuario_id = ?',
                           (alvo['id'], self.colaborador_id))
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]['valor'], 'Concordo')

    def test_resposta_aparece_marcada_ao_reabrir(self):
        alvo = self.perguntas[0]
        self.colaborador.post(f'/pesquisa/secao/{self.secao["id"]}',
                              data={f'pergunta_{alvo["id"]}': 'Concordo', 'acao': 'salvar_parcial'},
                              follow_redirects=True)
        html = self.colaborador.get(f'/pesquisa/secao/{self.secao["id"]}').get_data(as_text=True)
        marcado = re.search(r'value="Concordo"[^>]*checked|checked[^>]*value="Concordo"', html)
        self.assertIsNotNone(marcado, 'opcao salva nao veio marcada')

    def test_editar_substitui_sem_duplicar(self):
        alvo = self.perguntas[0]
        for valor in ('Concordo', 'Discordo'):
            self.colaborador.post(f'/pesquisa/secao/{self.secao["id"]}',
                                  data={f'pergunta_{alvo["id"]}': valor, 'acao': 'salvar_parcial'},
                                  follow_redirects=True)
        linhas = self._sql('SELECT valor FROM respostas WHERE pergunta_id = ? AND usuario_id = ?',
                           (alvo['id'], self.colaborador_id))
        self.assertEqual(len(linhas), 1, 'editar criou linha duplicada')
        self.assertEqual(linhas[0]['valor'], 'Discordo')

    def test_avanca_de_secao(self):
        dados = {f'pergunta_{p["id"]}': 'Concordo' for p in self.perguntas}
        r = self.colaborador.post(f'/pesquisa/secao/{self.secao["id"]}',
                                  data={**dados, 'acao': 'salvar_proximo'}, follow_redirects=False)
        self.assertEqual(r.status_code, 302)

    def test_obrigatoria_vazia_bloqueia_avanco(self):
        dados = {f'pergunta_{p["id"]}': 'Concordo' for p in self.perguntas}
        dados[f'pergunta_{self.perguntas[0]["id"]}'] = ''
        r = self.colaborador.post(f'/pesquisa/secao/{self.secao["id"]}',
                                  data={**dados, 'acao': 'salvar_proximo'}, follow_redirects=True)
        self.assertIn('responda', r.get_data(as_text=True).lower())


if __name__ == '__main__':
    unittest.main()
