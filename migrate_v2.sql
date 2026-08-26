-- ============================================
-- SCRIPT DE MIGRAÇÃO - v2
-- Adequa o banco existente às novas tabelas
-- Execute com cuidado em produção!
-- ============================================

-- 1. Criar tabela formularios
CREATE TABLE IF NOT EXISTS formularios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    descricao   TEXT,
    ativo       INTEGER NOT NULL DEFAULT 1,
    criado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Inserir formulário padrão (o que já existe nos dados)
INSERT OR IGNORE INTO formularios (id, nome, descricao, ativo)
VALUES (1, 'Pesquisa de Clima Vizca 2025', 'Formulário completo da pesquisa de clima organizacional.', 1);

-- 3. Adicionar formulario_id em secoes (se não existir)
-- SQLite não suporta ADD COLUMN IF NOT EXISTS, então usar try/catch via aplicação
-- Ou verificar antes:
-- PRAGMA table_info(secoes) para ver se a coluna já existe

CREATE TABLE IF NOT EXISTS secoes_nova (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    formulario_id   INTEGER NOT NULL DEFAULT 1,
    nome            TEXT NOT NULL,
    descricao       TEXT,
    ordem           INTEGER NOT NULL DEFAULT 0,
    ativo           INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (formulario_id) REFERENCES formularios(id) ON DELETE CASCADE
);

-- Copiar dados existentes
INSERT OR IGNORE INTO secoes_nova (id, formulario_id, nome, descricao, ordem, ativo)
SELECT id, 1, nome, descricao, ordem, ativo FROM secoes;

-- Remover tabela antiga e renomear
DROP TABLE IF EXISTS secoes;
ALTER TABLE secoes_nova RENAME TO secoes;

-- Recriar índice
CREATE INDEX IF NOT EXISTS idx_secoes_formulario ON secoes(formulario_id);

-- 4. Adicionar descricao em perguntas (se não existir)
-- Criar tabela临时 e copiar
CREATE TABLE IF NOT EXISTS perguntas_nova (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    secao_id            INTEGER NOT NULL,
    codigo              TEXT NOT NULL,
    texto               TEXT NOT NULL,
    descricao           TEXT,
    tipo                TEXT NOT NULL DEFAULT 'escala',
    obrigatoria         INTEGER NOT NULL DEFAULT 1,
    opcoes              TEXT,
    grid_rows           TEXT,
    ordem               INTEGER NOT NULL DEFAULT 0,
    condicional         INTEGER NOT NULL DEFAULT 0,
    condicao_pergunta   TEXT,
    condicao_valor      TEXT,
    ativo               INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (secao_id) REFERENCES secoes(id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO perguntas_nova (id, secao_id, codigo, texto, tipo, obrigatoria, opcoes, grid_rows, ordem, condicional, condicao_pergunta, condicao_valor, ativo)
SELECT id, secao_id, codigo, texto, tipo, obrigatoria, opcoes, grid_rows, ordem, condicional, condicao_pergunta, condicao_valor, ativo FROM perguntas;

DROP TABLE IF EXISTS perguntas;
ALTER TABLE perguntas_nova RENAME TO perguntas;

CREATE INDEX IF NOT EXISTS idx_perguntas_secao ON perguntas(secao_id);

-- 5. Adicionar formulario_id, data_inicio, data_fim em ciclos
CREATE TABLE IF NOT EXISTS ciclos_nova (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT NOT NULL,
    ano             INTEGER NOT NULL,
    formulario_id   INTEGER,
    data_inicio     TEXT,
    data_fim        TEXT,
    ativo           INTEGER NOT NULL DEFAULT 1,
    criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (formulario_id) REFERENCES formularios(id) ON DELETE SET NULL
);

INSERT OR IGNORE INTO ciclos_nova (id, nome, ano, formulario_id, data_inicio, data_fim, ativo, criado_em)
SELECT id, nome, ano, 1, NULL, NULL, ativo, criado_em FROM ciclos;

DROP TABLE IF EXISTS ciclos;
ALTER TABLE ciclos_nova RENAME TO ciclos;

-- 6. Adicionar usuario_id em respostas e mudar UNIQUE
CREATE TABLE IF NOT EXISTS respostas_nova (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ciclo_id        INTEGER NOT NULL,
    pergunta_id     INTEGER NOT NULL,
    usuario_id      INTEGER,
    valor           TEXT,
    comentario      TEXT,
    respondido_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ciclo_id) REFERENCES ciclos(id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES perguntas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE(ciclo_id, pergunta_id, usuario_id)
);

INSERT OR IGNORE INTO respostas_nova (id, ciclo_id, pergunta_id, valor, comentario, respondido_em)
SELECT id, ciclo_id, pergunta_id, valor, comentario, respondido_em FROM respostas;

DROP TABLE IF EXISTS respostas;
ALTER TABLE respostas_nova RENAME TO respostas;

CREATE INDEX IF NOT EXISTS idx_respostas_ciclo ON respostas(ciclo_id);
CREATE INDEX IF NOT EXISTS idx_respostas_pergunta ON respostas(pergunta_id);

-- 7. Recriar tabela respondentes (se não existir)
CREATE TABLE IF NOT EXISTS respondentes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ciclo_id    INTEGER NOT NULL,
    usuario_id  INTEGER NOT NULL,
    respondido_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ciclo_id, usuario_id),
    FOREIGN KEY (ciclo_id) REFERENCES ciclos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- FIM DA MIGRAÇÃO
