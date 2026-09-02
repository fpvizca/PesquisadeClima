-- ============================================
-- SCRIPT DE MIGRAÇÃO v3 - ANONIMATO TOTAL
-- Remove usuario_id das respostas
-- Execute: sqlite3 clima.db < migrate_v3.sql
-- ============================================

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- 1. Criar tabela formularios (se não existir)
CREATE TABLE IF NOT EXISTS formularios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    descricao   TEXT,
    ativo       INTEGER NOT NULL DEFAULT 1,
    criado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO formularios (id, nome, descricao, ativo)
VALUES (1, 'Pesquisa de Clima Vizca 2025', 'Formulário completo da pesquisa de clima.', 1);

-- 2. secoes: adicionar formulario_id (se não existir)
CREATE TABLE secoes_new (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    formulario_id   INTEGER NOT NULL DEFAULT 1,
    nome            TEXT NOT NULL,
    descricao       TEXT,
    ordem           INTEGER NOT NULL DEFAULT 0,
    ativo           INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (formulario_id) REFERENCES formularios(id) ON DELETE CASCADE
);
INSERT INTO secoes_new (id, formulario_id, nome, descricao, ordem, ativo)
SELECT id, 1, nome, descricao, ordem, ativo FROM secoes;
DROP TABLE secoes;
ALTER TABLE secoes_new RENAME TO secoes;
CREATE INDEX IF NOT EXISTS idx_secoes_formulario ON secoes(formulario_id);

-- 3. perguntas: adicionar descricao (se não existir)
CREATE TABLE perguntas_new (
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
INSERT INTO perguntas_new (id, secao_id, codigo, texto, tipo, obrigatoria, opcoes, grid_rows, ordem, condicional, condicao_pergunta, condicao_valor, ativo)
SELECT id, secao_id, codigo, texto, tipo, obrigatoria, opcoes, grid_rows, ordem, condicional, condicao_pergunta, condicao_valor, ativo FROM perguntas;
DROP TABLE perguntas;
ALTER TABLE perguntas_new RENAME TO perguntas;
CREATE INDEX IF NOT EXISTS idx_perguntas_secao ON perguntas(secao_id);

-- 4. ciclos: adicionar formulario_id, data_inicio, data_fim (se não existir)
CREATE TABLE ciclos_new (
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
INSERT INTO ciclos_new (id, nome, ano, formulario_id, data_inicio, data_fim, ativo, criado_em)
SELECT id, nome, ano, 1, NULL, NULL, ativo, criado_em FROM ciclos;
DROP TABLE ciclos;
ALTER TABLE ciclos_new RENAME TO ciclos;

-- 5. respostas: REMOVER usuario_id (anonimato total)
CREATE TABLE respostas_new (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ciclo_id        INTEGER NOT NULL,
    pergunta_id     INTEGER NOT NULL,
    valor           TEXT,
    comentario      TEXT,
    respondido_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ciclo_id) REFERENCES ciclos(id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES perguntas(id) ON DELETE CASCADE
);
INSERT INTO respostas_new (id, ciclo_id, pergunta_id, valor, comentario, respondido_em)
SELECT id, ciclo_id, pergunta_id, valor, comentario, respondido_em FROM respostas;
DROP TABLE respostas;
ALTER TABLE respostas_new RENAME TO respostas;
CREATE INDEX IF NOT EXISTS idx_respostas_ciclo ON respostas(ciclo_id);
CREATE INDEX IF NOT EXISTS idx_respostas_pergunta ON respostas(pergunta_id);

-- 6. Remover tabela respondentes (não mais necessária)
DROP TABLE IF EXISTS respondentes;

-- 7. Converter multipla_escolha sem opcoes para texto
UPDATE perguntas SET tipo = 'texto'
WHERE tipo = 'multipla_escolha' AND (opcoes IS NULL OR opcoes = '');

-- 8. Limpar duplicatas
DELETE FROM respostas WHERE id NOT IN (
    SELECT MAX(id) FROM respostas GROUP BY ciclo_id, pergunta_id
);

COMMIT;
PRAGMA foreign_keys = ON;
