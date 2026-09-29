"""Migrador do banco de dados.

Executa de forma idempotente:
  1. schema.sql  (CREATE TABLE IF NOT EXISTS - seguro)
  2. seed.sql    (apenas se a tabela usuarios estiver vazia)
  3. Colunas/c{tabelas} faltantes (substitui as migrations manuais v4 e v5)

As migrations migrate_v2.sql e migrate_v3.sql NAO sao executadas: elas recriam
tabelas de forma destrutiva e sao contraditorias entre si (v3 remove
respostas.usuario_id, que o schema atual utiliza). Banks novos ja nascem
corretos pelo schema.sql; bancos existentes ja têm v2/v3 aplicadas.

Uso:
    python migrar.py
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'clima.db'))

# Logins bloqueados: colaboradores sem mais de 3 meses de empresa
BLOQUEADOS = [
    'anderson.oliveira',
    'camila.macedo',
    'fernando.silva',
    'gabriel.melo',
    'isabelly.silva',
    'jailson.santos',
    'julia.santos',
    'lucca.seixas',
    'luciana.kurimori',
    'marianne.vieira',
    'samira.diniz',
]

MOTIVO_PADRAO = 'Menos de 3 meses de empresa'


def _colunas(db, tabela):
    return {r['name'] for r in db.execute(f'PRAGMA table_info({tabela})')}


def _tabelas(db):
    return {r['name'] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}


def _add_coluna(db, tabela, coluna, tipo):
    if coluna in _colunas(db, tabela):
        return False
    db.execute(f'ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}')
    return True


def aplicar(verbose=True):
    def log(msg):
        if verbose:
            print(msg)

    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    try:
        parent = os.path.dirname(DATABASE)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with open(os.path.join(BASE_DIR, 'schema.sql'), encoding='utf-8') as f:
            db.executescript(f.read())
        log('  [ok] schema.sql aplicado')

        total = db.execute('SELECT COUNT(*) AS c FROM usuarios').fetchone()['c']
        if total == 0:
            with open(os.path.join(BASE_DIR, 'seed.sql'), encoding='utf-8') as f:
                db.executescript(f.read())
            log('  [ok] seed.sql aplicado (banco estava vazio)')
        else:
            log(f'  [--] seed.sql ignorado ({total} usuarios existentes)')

        # --- Colunas adicionadas em migrate_v4.sql ---
        for col, tipo in (('titulo', 'TEXT'), ('texto_abertura', 'TEXT')):
            if _add_coluna(db, 'ciclos', col, tipo):
                log(f'  [ok] ciclos.{col} adicionada')
            else:
                log(f'  [--] ciclos.{col} ja existe')

        # --- Tabela de bloqueados (migrate_v5.sql) ---
        tabelas = _tabelas(db)
        if 'usuarios_bloqueados' not in tabelas:
            db.execute("""
                CREATE TABLE usuarios_bloqueados (
                  id         INTEGER PRIMARY KEY AUTOINCREMENT,
                  login      TEXT NOT NULL UNIQUE,
                  motivo     TEXT,
                  criado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            log('  [ok] tabela usuarios_bloqueados criada')
        else:
            log('  [--] tabela usuarios_bloqueados ja existe')

        for login in BLOQUEADOS:
            db.execute(
                'INSERT OR IGNORE INTO usuarios_bloqueados (login, motivo) VALUES (?, ?)',
                (login, MOTIVO_PADRAO)
            )
        n = db.execute('SELECT COUNT(*) AS c FROM usuarios_bloqueados').fetchone()['c']
        log(f'  [ok] {n} login(s) bloqueado(s)')

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f'ERRO: {e}')
        return False
    finally:
        db.close()


if __name__ == '__main__':
    print(f'Banco: {DATABASE}')
    print('Aplicando migracoes...')
    sys.exit(0 if aplicar() else 1)
