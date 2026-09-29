"""Infraestrutura compartilhada dos testes.

Os testes rodam sempre contra um banco temporario definido em DATABASE_PATH,
configurado ANTES de qualquer import de app/db (o modulo db le a variavel
na importacao). O Ollama e apontado para uma porta local recusada, para que
nenhum teste dependa da rede.
"""
import os
import sys
import shutil
import hashlib
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VALORES_ESCALA = [
    'Concordo totalmente',
    'Concordo',
    'Não concordo e nem discordo',
    'Discordo',
    'Discordo totalmente',
]

_tmp_global = None


def _preparar_ambiente():
    """Configura o ambiente uma vez por processo, antes dos imports do app."""
    global _tmp_global
    if _tmp_global is None:
        _tmp_global = tempfile.mkdtemp(prefix='clima_testes_')
        os.environ['DATABASE_PATH'] = os.path.join(_tmp_global, 'clima.db')
        os.environ['OLLAMA_BASE'] = 'http://127.0.0.1:9'
        if RAIZ not in sys.path:
            sys.path.insert(0, RAIZ)
    return _tmp_global


class BaseTeste(unittest.TestCase):
    """Base com app, clientes e usuarios de teste."""

    @classmethod
    def setUpClass(cls):
        _preparar_ambiente()
        import migrar
        migrar.aplicar(verbose=False)

        from app import app
        from db import get_db

        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SECRET_KEY'] = 'chave-de-teste' * 8
        cls.get_db = staticmethod(get_db)

        with app.app_context():
            db = get_db()
            # Garante que o admin exista com a senha conhecida
            db.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE login = 'admin'",
                (hash_sha256('admin123'),)
            )
            db.commit()

    def setUp(self):
        self.app.config['WTF_CSRF_ENABLED'] = False
        # Estado limpo: um ciclo ativo e NAO anonimizado. O banco e compartilhado
        # por todas as classes, entao cada teste precisa partir do mesmo ponto.
        self._garantir_ciclo_ativo()
        self.admin = self._login('admin', 'admin123')
        self.colaborador, self.colaborador_id = self._criar_colaborador('colaborador.teste')

    def _criar_colaborador(self, login, senha='senha123'):
        with self.app.app_context():
            db = self.get_db()
            db.execute('DELETE FROM usuarios WHERE login = ?', (login,))
            db.execute(
                'INSERT INTO usuarios (nome, email, login, senha_hash) VALUES (?,?,?,?)',
                ('Colaborador Teste', login + '@teste.local', login, hash_sha256(senha))
            )
            uid = db.execute('SELECT id FROM usuarios WHERE login = ?', (login,)).fetchone()['id']
            db.execute("INSERT OR IGNORE INTO usuario_roles (usuario_id, role) VALUES (?, 'colaborador')", (uid,))
            db.commit()
            return self._login(login, senha), uid

    def _login(self, login, senha):
        c = self.app.test_client()
        c.post('/login', data={'login': login, 'senha': senha}, follow_redirects=True)
        return c

    # atalhos de consulta
    def _sql(self, query, params=()):
        with self.app.app_context():
            return self.get_db().execute(query, params).fetchall()

    def _executar(self, query, params=()):
        with self.app.app_context():
            db = self.get_db()
            cur = db.execute(query, params)
            db.commit()
            return cur

    def _formulario_padrao(self):
        return self._sql('SELECT * FROM formularios ORDER BY id LIMIT 1')[0]

    def _ciclo_ativo(self):
        return self._sql('SELECT * FROM ciclos WHERE ativo = 1 ORDER BY id LIMIT 1')

    def _garantir_ciclo_ativo(self):
        self._executar('UPDATE ciclos SET ativo = 0, anonimizado_em = NULL')
        ciclo = self._sql('SELECT * FROM ciclos ORDER BY id LIMIT 1')
        if not ciclo:
            self._executar(
                "INSERT INTO ciclos (nome, ano, titulo, texto_abertura, ativo) VALUES ('Ciclo Teste', 2030, 'T', 'A', 1)"
            )
        else:
            self._executar('UPDATE ciclos SET ativo = 1 WHERE id = ?', (ciclo[0]['id'],))


def hash_sha256(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()
