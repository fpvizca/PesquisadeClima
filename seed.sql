-- ============================================
-- Seed: Pesquisa de Clima Vizca
-- ============================================

-- Admin (senha: admin123)
INSERT INTO usuarios (nome, email, login, senha_hash) VALUES
('Administrador', 'admin@vizca.com', 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
INSERT INTO usuario_roles (usuario_id, role) VALUES (1, 'admin');

-- Colaboradores de exemplo (senhas: 123456)
INSERT INTO usuarios (nome, email, login, senha_hash) VALUES
('João Silva', 'joao@vizca.com', 'joao', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
('Maria Santos', 'maria@vizca.com', 'maria', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
('Pedro Oliveira', 'pedro@vizca.com', 'pedro', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92');
INSERT INTO usuario_roles (usuario_id, role) VALUES (2, 'colaborador'), (3, 'colaborador'), (4, 'colaborador');

-- Ciclo ativo
INSERT INTO ciclos (nome, ano, ativo) VALUES ('Pesquisa de Clima 2025', 2025, 1);

-- ============================================
-- SEÇÕES
-- ============================================
INSERT INTO secoes (nome, descricao, ordem) VALUES
('Perfil', NULL, 1),
('Bem Estar', 'Queremos saber como você está.', 2),
('Diversidade e Inclusão', 'Vamos entender um pouco mais sobre os dois temas?', 3),
('Cultura Organizacional', 'A cultura organizacional é responsável por reunir os hábitos, comportamentos, crenças, valores éticos e morais e as políticas internas e externas da empresa.', 4),
('Desenvolvimento', NULL, 5),
('Valorização e Reconhecimento', NULL, 6),
('Crescimento Profissional', NULL, 7),
('Gestão e Liderança', NULL, 8),
('Funções Desempenhadas', NULL, 9),
('Relacionamento Equipe', NULL, 10),
('Comunicação', NULL, 11),
('Remuneração e Benefícios', NULL, 12),
('Infraestrutura e Ferramentas', NULL, 13),
('Mudanças', NULL, 14),
('Gerais', NULL, 15),
('Atuação em Projetos', 'Se você atua em outras instalações, como por exemplo, instalações do cliente, gostaríamos de entender qual a sua percepção em relação ao clima no seu ambiente de trabalho. Caso não se encaixe nesta situação, selecione a opção N/A - Não Aplicável.', 16);

-- ============================================
-- PERGUNTAS - SEÇÃO 1: PERFIL
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(1, 'Q1', 'Qual é a sua faixa etária?', 'multipla_escolha', 1, '["Até 35 anos","De 36 a 49 anos","50 anos ou mais"]', 1),
(1, 'Q2', 'Qual o seu nível de escolaridade?', 'multipla_escolha', 1, '["Médio completo","Superior Incompleto","Superior Completo","Especialização/Mestrado (cursando ou completo)","Doutorado (cursando ou completo)","Pós-Doutorado (cursando ou completo)"]', 2),
(1, 'Q3', 'Há quanto tempo você atua na empresa?', 'multipla_escolha', 1, '["6 meses a 2 anos","De 2 a 5 anos","Mais de 5 anos"]', 3);

-- ============================================
-- PERGUNTAS - SEÇÃO 2: BEM ESTAR
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(2, 'Q4', 'Atualmente com qual das situações abaixo você mais se preocupa?', 'multipla_escolha', 1, '["Saúde física","Saúde emocional e mental","Segurança","Realização pessoal","Relações familiares","Relações sociais","Finanças"]', 1),
(2, 'Q5', 'Tenho hábitos alimentares saudáveis no meu dia a dia', 'escala', 1, NULL, 2),
(2, 'Q6', 'Pratico exercícios físicos regularmente', 'escala', 1, NULL, 3),
(2, 'Q7', 'Tiro férias anualmente', 'escala', 1, NULL, 4),
(2, 'Q8', 'Se você respondeu "DISCORDO TOTALMENTE" ou "DISCORDO" na afirmação anterior, nos conte o motivo:', 'paragrafo', 0, NULL, 5),
(2, 'Q9', 'Se você respondeu "CONCORDO TOTALMENTE" ou "CONCORDO" na afirmação anterior, como você tem usufruído desse período de descanso?', 'multipla_escolha', 0, '["Tiro os dias de férias de forma ininterrupta (ex.: 30, 20 dias diretos)","Tiro os dias de férias em dois períodos (ex.: 02 intervalos entre um determinado período de meses)","Tiro os dias de férias de forma fracionada (vários dias ao longo do ano até finalizar o saldo de dias)"]', 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 3: DIVERSIDADE E INCLUSÃO
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(3, 'Q10', 'Como você se reconhece em relação ao seu gênero?', 'multipla_escolha', 1, '["Cisgênero","Transgênero","Não-binário","Prefiro não dizer"]', 1),
(3, 'Q11', 'A empresa oferece oportunidades e tratamento igualitários para todos, proporcionando um ambiente de trabalho livre de preconceito e desigualdade, independente dos fatores:', 'grid', 1, '["Concordo totalmente","Concordo","Não concordo e nem discordo","Discordo","Discordo totalmente"]', 2),
(3, 'Q12', 'Independente da minha origem, idade, raça, experiências, personalidade, religião e orientação sexual, sou respeitado e acolhido pelo meu gestor e minha equipe de trabalho', 'escala', 1, NULL, 3),
(3, 'Q13', 'A empresa demonstra uma visão ampla e atrativa para todos, respeita as diferenças e valoriza a pluralidade', 'escala', 1, NULL, 4),
(3, 'Q14', 'A empresa trata de forma adequada situações que envolvem preconceito, discriminação ou condutas fora de sua cultura', 'escala', 1, NULL, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 4: CULTURA ORGANIZACIONAL
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(4, 'Q15', 'Me identifico com a Cultura Organizacional da Vizca', 'escala', 1, NULL, 1),
(4, 'Q16', 'Os valores propagados pela Vizca são realmente colocados em prática', 'escala', 1, NULL, 2),
(4, 'Q17', 'Me sinto pertencente à Vizca', 'escala', 1, NULL, 3),
(4, 'Q18', 'A Vizca é um bom lugar para se trabalhar', 'escala', 1, NULL, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 5: DESENVOLVIMENTO
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(5, 'Q19', 'A empresa proporciona condições de desenvolvimento para que eu tenha um aprendizado contínuo', 'escala', 1, NULL, 1),
(5, 'Q20', 'Estou satisfeito com os estímulos de desenvolvimento oferecidos pela empresa (Ex.: PDI e PDO).', 'escala', 1, NULL, 2),
(5, 'Q21', 'Tenho oportunidade de sugerir e negociar meu plano de desenvolvimento', 'escala', 1, NULL, 3),
(5, 'Q22', 'Tenho oportunidade de aplicar meus conhecimentos no meu trabalho', 'escala', 1, NULL, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 6: VALORIZAÇÃO E RECONHECIMENTO
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(6, 'Q23', 'Tenho oportunidade de desenvolvimento profissional na empresa', 'escala', 1, NULL, 1),
(6, 'Q24', 'Dentro do possível, tenho liberdade para fazer o meu trabalho da forma que considero melhor', 'escala', 1, NULL, 2),
(6, 'Q25', 'Meu potencial de realização profissional têm sido adequadamente aproveitado', 'escala', 1, NULL, 3),
(6, 'Q26', 'Tenho autonomia para propor melhorias na execução do meu trabalho', 'escala', 1, NULL, 4),
(6, 'Q27', 'Minhas ideias e sugestões são ouvidas', 'escala', 1, NULL, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 7: CRESCIMENTO PROFISSIONAL
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(7, 'Q28', 'A empresa proporciona espaço e estimula o crescimento profissional', 'escala', 1, NULL, 1),
(7, 'Q29', 'Tenho interesse em assumir novos desafios e responsabilidades na empresa', 'escala', 1, NULL, 2),
(7, 'Q30', 'Entendo quais são os requisitos necessários para ocupar outras posições na empresa', 'escala', 1, NULL, 3);

-- ============================================
-- PERGUNTAS - SEÇÃO 8: GESTÃO E LIDERANÇA
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(8, 'Q31', 'As orientações que a empresa fornece para realização do trabalho são claras e objetivas', 'escala', 1, NULL, 1),
(8, 'Q32', 'Recebo informações regulares sobre o meu desempenho', 'escala', 1, NULL, 2),
(8, 'Q33', 'Há espaço para que eu contribua com as tomadas de decisão do meu gestor ou responsável imediato', 'escala', 1, NULL, 3),
(8, 'Q34', 'Minhas entregas são reconhecidas pelo meu gestor', 'escala', 1, NULL, 4),
(8, 'Q35', 'Recebo suporte necessário para a realização do meu trabalho', 'escala', 1, NULL, 5),
(8, 'Q36', 'Me sinto à vontade para solicitar ou dar feedback ao meu gestor', 'escala', 1, NULL, 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 9: FUNÇÕES DESEMPENHADAS
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(9, 'Q37', 'Estou satisfeito com as funções que desempenho no meu dia a dia', 'escala', 1, NULL, 1),
(9, 'Q38', 'Entendo a importância das minhas atividades para os objetivos da organização', 'escala', 1, NULL, 2),
(9, 'Q39', 'Consigo cumprir minhas atividades de trabalho sem sobrecarga', 'escala', 1, NULL, 3),
(9, 'Q40', 'A empresa realiza ações de prevenção e controle em resposta a possíveis impactos relacionados à sobrecarga/demandas excessivas', 'escala', 1, NULL, 4),
(9, 'Q41', 'Tenho tempo suficiente para realizar minhas atividades', 'escala', 1, NULL, 5),
(9, 'Q42', 'Me sinto desafiado (positivamente) no meu trabalho', 'escala', 1, NULL, 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 10: RELACIONAMENTO EQUIPE
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(10, 'Q43', 'Me sinto confortável com minha equipe de trabalho', 'escala', 1, NULL, 1),
(10, 'Q44', 'Meu ambiente de trabalho é de cooperação e respeito', 'escala', 1, NULL, 2),
(10, 'Q45', 'No meu grupo de trabalho as pessoas se relacionam de forma harmoniosa', 'escala', 1, NULL, 3),
(10, 'Q46', 'Meus colegas estão comprometidos com os objetivos do trabalho', 'escala', 1, NULL, 4),
(10, 'Q47', 'Acredito que seja possível criar laços de amizade no ambiente de trabalho', 'escala', 1, NULL, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 11: COMUNICAÇÃO
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(11, 'Q48', 'A comunicação INSTITUCIONAL (política, códigos, objetivos, missão, visão, valores) é clara e objetiva', 'escala', 1, NULL, 1),
(11, 'Q49', 'A comunicação INTERNA (avisos, comunicados, mudanças, etc.) é clara e objetiva', 'escala', 1, NULL, 2),
(11, 'Q50', 'A comunicação de papéis e responsabilidades dentro da empresa é clara e objetiva', 'escala', 1, NULL, 3),
(11, 'Q51', 'A comunicação no dia a dia de trabalho é clara e facilita o entendimento mútuo.', 'escala', 1, NULL, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 12: REMUNERAÇÃO E BENEFÍCIOS
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(12, 'Q52', 'Estou satisfeito com minha remuneração', 'escala', 1, NULL, 1),
(12, 'Q53', 'Nos ajude a entender melhor a resposta anterior:', 'texto', 0, NULL, 2),
(12, 'Q54', 'Meu salário é justo para as atividades que desempenho', 'escala', 1, NULL, 3),
(12, 'Q55', 'Nos ajude a entender melhor a resposta anterior:', 'texto', 0, NULL, 4),
(12, 'Q56', 'Estou satisfeito com os benefícios oferecidos pela empresa. São exemplos de benefícios: seguro de vida, wellhub/gympass, plr, VR/VA, convênio odontológico, convênio médico e VT. *Aplicável aos CLTs.', 'escala', 1, NULL, 5),
(12, 'Q57', 'Nos ajude a entender melhor a resposta anterior:', 'texto', 0, NULL, 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 13: INFRAESTRUTURA E FERRAMENTAS
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(13, 'Q58', 'Considero meu ambiente de trabalho seguro (organização, limpeza, revisões e manutenções em dia).', 'escala', 1, NULL, 1),
(13, 'Q59', 'Estou satisfeito com o conforto físico (temperatura, luminosidade)', 'escala', 1, NULL, 2),
(13, 'Q60', 'Os equipamentos fornecidos atendem as necessidades para o desenvolvimento da minha função', 'escala', 1, NULL, 3),
(13, 'Q61', 'A empresa disponibiliza equipamentos de qualidade. Exemplos de equipamentos: notebook, computador, teclado, mouse, suporte para o notebook)', 'escala', 1, NULL, 4),
(13, 'Q62', 'A empresa investe adequadamente em infraestrutura e tecnologia para apoiar o meu trabalho', 'escala', 1, NULL, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 14: MUDANÇAS
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(14, 'Q63', 'Como me sinto atualmente em relação às mudanças, tanto internas como externas (na empresa, nos clientes e no mercado)?', 'paragrafo', 1, NULL, 1),
(14, 'Q64', 'Me sinto à vontade para compartilhar com o meu gestor, minhas preocupações em relação ao meu futuro na empresa', 'escala', 1, NULL, 2),
(14, 'Q65', 'A empresa está preocupada em garantir a estabilidade dos colaboradores', 'escala', 1, NULL, 3),
(14, 'Q66', 'A empresa está reagindo positivamente às mudanças, adotando novas estratégias e buscando novas oportunidades, para manter o seu desempenho e competitividade no mercado', 'escala', 1, NULL, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 15: GERAIS
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(15, 'Q67', 'O que mais te CONECTA à Vizca?', 'texto', 1, NULL, 1),
(15, 'Q68', 'O que mais te DESCONECTA da Vizca?', 'texto', 1, NULL, 2),
(15, 'Q69', 'Você identifica alguma situação ou incômodo presente?', 'paragrafo', 0, NULL, 3),
(15, 'Q70', 'Alguma ideia ou sugestão para a diretoria?', 'paragrafo', 0, NULL, 4),
(15, 'Q71', 'Existe algum ponto de atenção que você gostaria de comentar?', 'paragrafo', 0, NULL, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 16: ATUAÇÃO EM PROJETOS
-- ============================================
INSERT INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(16, 'Q72', 'No ambiente onde atuo, o clima é satisfatório, contribuindo para o meu engajamento, motivação e o desempenho.', 'multipla_escolha', 1, '["Concordo Totalmente","Concordo","Não concordo e nem discordo","Discordo","Discordo Totalmente","N/A - Não aplicável"]', 1),
(16, 'Q73', 'Se desejar, compartilhe os principais fatores que amparam sua resposta.', 'texto', 0, NULL, 2),
(16, 'Q74', 'Se desejar, compartilhe o nome do projeto que você atua', 'texto', 0, NULL, 3);
