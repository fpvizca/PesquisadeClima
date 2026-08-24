-- ============================================
-- SEED DATA - APENAS PARA AMBIENTE DE TESTE/DESENVOLVIMENTO
-- ============================================
-- ATENCAO: Nao execute este script em producao.
-- Ele contem dados ficticios (usuarios, projetos, etc.)
-- ============================================

-- Seed: usuarios (senha padrao: admin123)
INSERT OR IGNORE INTO usuarios (id, nome, login, email, senha_hash) VALUES (1, 'Administrador', 'admin', 'admin@empresa.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');

-- Seed: roles (apenas admin)
INSERT OR IGNORE INTO usuario_roles (usuario_id, role) VALUES (1, 'admin');

-- Colaboradores de exemplo (senhas: 123456)
INSERT OR IGNORE INTO usuarios (id, nome, login, email, senha_hash) VALUES
(2, 'João Silva', 'joao', 'joao@vizca.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
(3, 'Maria Santos', 'maria', 'maria@vizca.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
(4, 'Pedro Oliveira', 'pedro', 'pedro@vizca.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92');
INSERT OR IGNORE INTO usuario_roles (usuario_id, role) VALUES (2, 'colaborador'), (3, 'colaborador'), (4, 'colaborador');

-- Ciclo ativo
INSERT OR IGNORE INTO ciclos (id, nome, ano, ativo) VALUES (1, 'Pesquisa de Clima 2025', 2025, 1);

-- ============================================
-- SEÇÕES
-- ============================================
INSERT OR IGNORE INTO secoes (nome, descricao, ordem) VALUES
('Perfil', NULL, 1),
('Bem Estar', 'Queremos saber como você está.', 2),
('Diversidade e Inclusão', 'Vamos entender um pouco mais sobre os dois temas?', 3),
('Cultura Organizacional', 'A cultura organizacional é responsável por reunir os hábitos, comportamentos, crenças, valores éticos e morais e as políticas internas e externas da empresa.', 4),
('Desenvolvimento', NULL, 5),
('Valorização e Reconhecimento', NULL, 6),
('Crescimento Profissional', NULL, 7),
('Liderança', NULL, 8),
('Comunicação', NULL, 9),
('Clareza de Objetivos', NULL, 10),
('Recursos e Infraestrutura', NULL, 11),
('Autonomia e Empoderamento', NULL, 12),
('Clima e Ambiente de Trabalho', NULL, 13),
('Justiça e Transparência', NULL, 14),
('Qualidade do Serviço', NULL, 15),
('Sugestões e Comentários', 'Espaço livre para suas sugestões e comentários.', 16);

-- ============================================
-- PERGUNTAS (74 questões)
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(1, 'Q1', 'Qual sua idade?', 'multipla_escolha', 1, 1),
(1, 'Q2', 'Qual seu gênero?', 'multipla_escolha', 1, 2),
(1, 'Q3', 'Há quanto tempo você trabalha na empresa?', 'multipla_escolha', 1, 3),
(2, 'Q4', 'Sinto-me seguro(a) para expresar minhas ideias e opiniões no trabalho.', 'escala', 1, 1),
(2, 'Q5', 'Sinto que meu trabalho é valorizado pela liderança.', 'escala', 1, 2),
(2, 'Q6', 'Consigo equilibrar minha vida pessoal e profissional.', 'escala', 1, 3),
(2, 'Q7', 'A empresa se preocupa com meu bem-estar físico e mental.', 'escala', 1, 4),
(2, 'Q8', 'Sinto que posso ser eu mesmo(a) no ambiente de trabalho.', 'escala', 1, 5),
(2, 'Q9', 'Tenho acesso a recursos que me ajudam a cuidar da minha saúde.', 'escala', 1, 6),
(3, 'Q10', 'A empresa valoriza e respeita as diferenças entre os colaboradores.', 'escala', 1, 1),
(3, 'Q11', 'Sinto que pertenço a um ambiente inclusivo.', 'escala', 1, 2),
(3, 'Q12', 'Todos têm as mesmas oportunidades de crescimento, independentemente de suas características.', 'escala', 1, 3),
(3, 'Q13', 'A empresa promove ações de conscientização sobre diversidade.', 'escala', 1, 4),
(3, 'Q14', 'Sinto-me respeitado(a) pelos colegas e pela liderança.', 'escala', 1, 5),
(4, 'Q15', 'Conheço e compartilho os valores da empresa.', 'escala', 1, 1),
(4, 'Q16', 'A empresa cumpre o que promete aos colaboradores.', 'escala', 1, 2),
(4, 'Q17', 'Sinto que há confiança entre os colaboradores e a liderança.', 'escala', 1, 3),
(4, 'Q18', 'A empresa estimula a inovação e a melhoria contínua.', 'escala', 1, 4),
(4, 'Q19', 'Sinto que faço parte de algo maior.', 'escala', 1, 5),
(5, 'Q20', 'Recebo feedbacks construtivos que me ajudam a crescer.', 'escala', 1, 1),
(5, 'Q21', 'Tenho oportunidades de aprender coisas novas.', 'escala', 1, 2),
(5, 'Q22', 'A empresa investe no desenvolvimento profissional dos colaboradores.', 'escala', 1, 3),
(5, 'Q23', 'Sinto que estou evoluindo profissionalmente.', 'escala', 1, 4),
(5, 'Q24', 'Recebo treinamentos adequados para minha função.', 'escala', 1, 5),
(6, 'Q25', 'Meus resultados e contribuições são reconhecidos pela empresa.', 'escala', 1, 1),
(6, 'Q26', 'A empresa valoriza o trabalho em equipe.', 'escala', 1, 2),
(6, 'Q27', 'Sinto que meu esforço faz a diferença.', 'escala', 1, 3),
(6, 'Q28', 'Recebo feedbacks positivos quando faço um bom trabalho.', 'escala', 1, 4),
(6, 'Q29', 'A empresa tem programas de reconhecimento para os colaboradores.', 'escala', 1, 5),
(7, 'Q30', 'Tenho perspectivas de crescimento na empresa.', 'escala', 1, 1),
(7, 'Q31', 'Conheço os caminhos de carreira disponíveis.', 'escala', 1, 2),
(7, 'Q32', 'A empresa promove oportunidades de promoção interna.', 'escala', 1, 3),
(7, 'Q33', 'Sinto que posso crescer profissionalmente aqui.', 'escala', 1, 4),
(7, 'Q34', 'A empresa valoriza a experiência e o conhecimento dos colaboradores.', 'escala', 1, 5),
(8, 'Q35', 'Minha liderança é clara nas suas orientações.', 'escala', 1, 1),
(8, 'Q36', 'Sinto que posso confiar na minha liderança.', 'escala', 1, 2),
(8, 'Q37', 'Minha liderança ouve e considera minhas ideias.', 'escala', 1, 3),
(8, 'Q38', 'A liderança age com integridade e exemplo.', 'escala', 1, 4),
(8, 'Q39', 'Minha liderança me dá autonomia para executar meu trabalho.', 'escala', 1, 5),
(8, 'Q40', 'Sinto que a liderança se preocupa com o desenvolvimento da equipe.', 'escala', 1, 6),
(9, 'Q41', 'Consigo me comunicar bem com meus colegas.', 'escala', 1, 1),
(9, 'Q42', 'As informações importantes chegam até mim no tempo certo.', 'escala', 1, 2),
(9, 'Q43', 'Sinto que posso expressar minhas ideias com clareza.', 'escala', 1, 3),
(9, 'Q44', 'A empresa usa canais eficazes de comunicação interna.', 'escala', 1, 4),
(9, 'Q45', 'Sinto que há transparência nas informações da empresa.', 'escala', 1, 5),
(10, 'Q46', 'Sei exatamente o que é esperado de mim no trabalho.', 'escala', 1, 1),
(10, 'Q47', 'Tenho clareza sobre os objetivos da empresa.', 'escala', 1, 2),
(10, 'Q48', 'Minha liderança define metas claras para mim.', 'escala', 1, 3),
(10, 'Q49', 'Sinto que meu trabalho contribui para os objetivos da empresa.', 'escala', 1, 4),
(10, 'Q50', 'Tenho clareza sobre as prioridades do meu trabalho.', 'escala', 1, 5),
(11, 'Q51', 'Tenho os materiais e ferramentas necessários para fazer meu trabalho bem feito.', 'escala', 1, 1),
(11, 'Q52', 'O ambiente de trabalho é limpo e organizado.', 'escala', 1, 2),
(11, 'Q53', 'Tenho acesso à tecnologia necessária para minha função.', 'escala', 1, 3),
(11, 'Q54', 'A empresa provisiona recursos adequados para o desenvolvimento das atividades.', 'escala', 1, 4),
(11, 'Q55', 'Sinto que a empresa investe em infraestrutura.', 'escala', 1, 5),
(11, 'Q56', 'Tenho condições físicas adequadas para trabalhar.', 'escala', 1, 6),
(12, 'Q57', 'Tenho liberdade para tomar decisões no meu trabalho.', 'escala', 1, 1),
(12, 'Q58', 'Sinto que sou responsável pelos meus resultados.', 'escala', 1, 2),
(12, 'Q59', 'A empresa confia no meu trabalho.', 'escala', 1, 3),
(12, 'Q60', 'Posso propor melhorias sem medo de represálias.', 'escala', 1, 4),
(12, 'Q61', 'Sinto que tenho autonomia para fazer meu trabalho.', 'escala', 1, 5),
(13, 'Q62', 'O ambiente de trabalho é agradável.', 'escala', 1, 1),
(13, 'Q63', 'Sinto que há respeito entre os colegas.', 'escala', 1, 2),
(13, 'Q64', 'O clima organizacional é positivo.', 'escala', 1, 3),
(13, 'Q65', 'Sinto que faço parte de uma equipe unida.', 'escala', 1, 4),
(13, 'Q66', 'Gosto de vir trabalhar todos os dias.', 'escala', 1, 5),
(14, 'Q67', 'A empresa trata todos os colaboradores de forma justa.', 'escala', 1, 1),
(14, 'Q68', 'As decisões da empresa são tomadas de forma transparente.', 'escala', 1, 2),
(14, 'Q69', 'Sinto que há igualdade de oportunidades.', 'escala', 1, 3),
(14, 'Q70', 'A empresa cumpre suas promessas.', 'escala', 1, 4),
(14, 'Q71', 'Sinto que sou tratado(a) com justiça.', 'escala', 1, 5),
(15, 'Q72', 'Estou satisfeito(a) com a qualidade do meu trabalho.', 'escala', 1, 1),
(15, 'Q73', 'Sinto que faço um trabalho de qualidade.', 'escala', 1, 2),
(15, 'Q74', 'Tenho orgulho do trabalho que realizo.', 'escala', 1, 3);

-- Perguntas abertas da seção 16
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(16, 'Q75', 'O que você mais gosta na empresa?', 'paragrafo', 0, 1),
(16, 'Q76', 'O que você gostaria que mudasse na empresa?', 'paragrafo', 0, 2),
(16, 'Q77', 'Alguma sugestão ou comentário adicional?', 'paragrafo', 0, 3);
