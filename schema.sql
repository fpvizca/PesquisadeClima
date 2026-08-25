-- ============================================
-- Schema: Pesquisa de Clima Vizca
-- ============================================

CREATE TABLE IF NOT EXISTS usuarios (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  id_externo    INTEGER UNIQUE,
  login         TEXT,
  nome          TEXT NOT NULL,
  email         TEXT,
  senha_hash    TEXT NOT NULL,
  ativo         INTEGER NOT NULL DEFAULT 1,
  criado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuario_roles (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id  INTEGER NOT NULL,
  role        TEXT NOT NULL CHECK (role IN ('colaborador','gestor','diretoria','admin')),
  criado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (usuario_id, role),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS formularios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    descricao   TEXT,
    ativo       INTEGER NOT NULL DEFAULT 1,
    criado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS secoes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    formulario_id   INTEGER NOT NULL,
    nome            TEXT NOT NULL,
    descricao       TEXT,
    ordem           INTEGER NOT NULL DEFAULT 0,
    ativo           INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (formulario_id) REFERENCES formularios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS perguntas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    secao_id        INTEGER NOT NULL,
    codigo          TEXT NOT NULL,
    texto           TEXT NOT NULL,
    descricao       TEXT,
    tipo            TEXT NOT NULL DEFAULT 'escala' CHECK (tipo IN ('escala', 'multipla_escolha', 'texto', 'paragrafo', 'grid')),
    obrigatoria     INTEGER NOT NULL DEFAULT 1,
    opcoes          TEXT,
    grid_rows       TEXT,
    ordem           INTEGER NOT NULL DEFAULT 0,
    ativo           INTEGER NOT NULL DEFAULT 1,
    condicional     INTEGER NOT NULL DEFAULT 0,
    condicao_pergunta TEXT,
    condicao_valor  TEXT,
    FOREIGN KEY (secao_id) REFERENCES secoes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ciclos (
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

CREATE TABLE IF NOT EXISTS respostas (
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

CREATE TABLE IF NOT EXISTS respondentes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ciclo_id        INTEGER NOT NULL,
    usuario_id      INTEGER NOT NULL,
    respondido_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ciclo_id) REFERENCES ciclos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE(ciclo_id, usuario_id)
);

CREATE INDEX IF NOT EXISTS idx_usuario_roles_usuario ON usuario_roles(usuario_id);
CREATE INDEX IF NOT EXISTS idx_secoes_formulario ON secoes(formulario_id);
CREATE INDEX IF NOT EXISTS idx_perguntas_secao ON perguntas(secao_id);
CREATE INDEX IF NOT EXISTS idx_respostas_ciclo ON respostas(ciclo_id);
CREATE INDEX IF NOT EXISTS idx_respostas_pergunta ON respostas(pergunta_id);
CREATE INDEX IF NOT EXISTS idx_respondentes_ciclo ON respondentes(ciclo_id);
CREATE INDEX IF NOT EXISTS idx_respondentes_usuario ON respondentes(usuario_id);
