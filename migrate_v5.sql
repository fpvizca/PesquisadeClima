-- ============================================
-- Migration v5: Bloqueio de colaboradores
-- ============================================

CREATE TABLE IF NOT EXISTS usuarios_bloqueados (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  login         TEXT NOT NULL UNIQUE,
  motivo        TEXT,
  criado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO usuarios_bloqueados (login, motivo) VALUES
  ('anderson.oliveira', 'Menos de 3 meses de empresa'),
  ('camila.macedo',      'Menos de 3 meses de empresa'),
  ('fernando.silva',     'Menos de 3 meses de empresa'),
  ('gabriel.melo',       'Menos de 3 meses de empresa'),
  ('isabelly.silva',     'Menos de 3 meses de empresa'),
  ('jailson.santos',     'Menos de 3 meses de empresa'),
  ('julia.santos',       'Menos de 3 meses de empresa'),
  ('lucca.seixas',       'Menos de 3 meses de empresa'),
  ('luciana.kurimori',   'Menos de 3 meses de empresa'),
  ('marianne.vieira',    'Menos de 3 meses de empresa'),
  ('samira.diniz',       'Menos de 3 meses de empresa');
