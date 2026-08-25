-- ============================================
-- SEED DATA - APENAS PARA AMBIENTE DE TESTE/DESENVOLVIMENTO
-- ============================================
-- ATENCAO: Nao execute este script em producao.
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

-- Formulário padrão
INSERT OR IGNORE INTO formularios (id, nome, descricao, ativo) VALUES (1, 'Pesquisa de Clima Vizca 2025', 'Formulário completo da pesquisa de clima organizacional com 16 seções e 74 perguntas.', 1);

-- Ciclo ativo (vinculado ao formulário)
INSERT OR IGNORE INTO ciclos (id, nome, ano, formulario_id, data_inicio, data_fim, ativo) VALUES (1, 'Pesquisa de Clima 2025', 2025, 1, '2025-08-01', '2025-09-30', 1);

-- ============================================
-- SEÇÕES (16 seções do Google Forms) - Vinculadas ao formulário 1
-- ============================================
INSERT OR IGNORE INTO secoes (id, formulario_id, nome, descricao, ordem) VALUES
(1, 1, 'Perfil', 'Você não precisa se identificar, mas nos ajude a saber um pouco sobre o seu perfil.', 1),
(2, 1, 'Bem Estar', 'Queremos saber como você está.', 2),
(3, 1, 'Diversidade e Inclusão', '<p class="mb-2">Vamos entender um pouco mais sobre os dois temas?</p><hr class="my-2"><p><strong>DIVERSIDADE:</strong> A diversidade está relacionada ao conceito de pluralidade, ou seja, características, comportamentos e valores que tornam as pessoas únicas. Diversidade pode ser entendida como quaisquer características que diferem as pessoas uma das outras. Também significa multiplicidade e variedade, estando ela relacionada a todos os atributos que caracterizam ou diferenciam os indivíduos dentro de uma sociedade.</p><p class="mb-0">Essas características podem ser físicas ou até mesmo de personalidade.</p><hr class="my-2"><p><strong>INCLUSÃO:</strong> O conceito de inclusão é a capacidade de entender e reconhecer o outro que é diferente em um ou vários aspectos, respeitando suas pluralidades e o integrando no ambiente. A inclusão é o ato de criar espaços saudáveis para pessoas com aspectos diferentes do seu, aceitando e lidando com as diferenças. Deste modo, é possível adaptar o ambiente para que todos que estejam presentes sejam respeitados e consigam conviver independente das singularidades.</p><hr class="my-2"><p class="mb-0"><em>Agora que você já sabe mais sobre os temas, nos ajude a entender qual é a sua percepção em relação à integração da diversidade e inclusão em nosso ambiente organizacional.</em></p>', 3),
(4, 1, 'Cultura Organizacional', 'A cultura organizacional é responsável por reunir os hábitos, comportamentos, crenças, valores éticos e morais e as políticas internas e externas da empresa.', 4),
(5, 1, 'Desenvolvimento', NULL, 5),
(6, 1, 'Valorização e Reconhecimento', NULL, 6),
(7, 1, 'Crescimento Profissional', NULL, 7),
(8, 1, 'Gestão e Liderança', NULL, 8),
(9, 1, 'Funções Desempenhadas', NULL, 9),
(10, 1, 'Relacionamento Equipe', NULL, 10),
(11, 1, 'Comunicação', NULL, 11),
(12, 1, 'Remuneração e Benefícios', NULL, 12),
(13, 1, 'Infraestrutura e Ferramentas de Trabalho', NULL, 13),
(14, 1, 'Mudanças', NULL, 14),
(15, 1, 'Gerais', 'Espaço livre para suas sugestões e comentários.', 15),
(16, 1, 'Atuação em Projetos', NULL, 16);

-- ============================================
-- PERGUNTAS - SEÇÃO 1: PERFIL
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(1, 'Q1', 'Qual é a sua faixa etária?', 'multipla_escolha', 1, 'Até 35 anos, De 36 a 49 anos, 50 anos ou mais', 1),
(1, 'Q2', 'Qual o seu nível de escolaridade?', 'multipla_escolha', 1, 'Médio completo, Superior Incompleto, Superior Completo, Especialização/Mestrado (cursando ou completo), Doutorado (cursando ou completo), Pós-Doutorado (cursando ou completo)', 2),
(1, 'Q3', 'Há quanto tempo você atua na empresa?', 'multipla_escolha', 1, '6 meses a 2 anos, De 2 a 5 anos, Mais de 5 anos', 3);

-- ============================================
-- PERGUNTAS - SEÇÃO 2: BEM ESTAR
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(2, 'Q4', 'Atualmente com qual das situações abaixo você mais se preocupa?', 'multipla_escolha', 1, 'Saúde física, Saúde emocional e mental, Segurança, Realização pessoal, Relações familiares, Relações sociais, Finanças', 1);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(2, 'Q5', 'Tenho hábitos alimentares saudáveis no meu dia a dia', 'escala', 1, 2),
(2, 'Q6', 'Pratico exercícios físicos regularmente', 'escala', 1, 3),
(2, 'Q7', 'Tiro férias anualmente', 'escala', 1, 4);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, condicional, condicao_pergunta, condicao_valor, ordem) VALUES
(2, 'Q8', 'Se você respondeu "DISCORDO TOTALMENTE" ou "DISCORDO" na afirmação anterior, nos conte o motivo:', 'paragrafo', 0, 1, 'Q7', 'Discordo|Discordo totalmente', 5);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, condicional, condicao_pergunta, condicao_valor, ordem) VALUES
(2, 'Q9', 'Se você respondeu "CONCORDO TOTALMENTE" ou "CONCORDO" na afirmação anterior, como você tem usufruído desse período de descanso?', 'multipla_escolha', 0, 'Tiro os dias de férias de forma ininterrupta (ex.: 30, 20 dias diretos), Tiro os dias de férias em dois períodos (ex.: 02 intervalos entre um determinado período de meses), Tiro os dias de férias de forma fracionada (vários dias ao longo do ano até finalizar o saldo de dias)', 1, 'Q7', 'Concordo totalmente|Concordo', 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 3: DIVERSIDADE E INCLUSÃO
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, descricao, tipo, obrigatoria, opcoes, ordem) VALUES
(3, 'Q10', 'Como você se reconhece em relação ao seu gênero?', '<p class="mb-2"><strong>Cisgênero:</strong> o cisgênero consiste no indivíduo que se identifica com o seu "gênero de nascença". Por exemplo: um indivíduo que possui características biológicas típicas do sexo masculino e que se identifica (social e psicologicamente) como um homem.</p><p class="mb-2"><strong>Transgênero:</strong> o transgênero é o indivíduo que se identifica com um gênero diferente daquele que lhe foi atribuído no nascimento. Por exemplo: uma pessoa que nasce com características biológicas masculinas, mas que se sente do gênero feminino.</p><p class="mb-0"><strong>Não-binário:</strong> o não-binário é a classificação que caracteriza a mistura entre masculino e feminino, ou a total indiferença a ambos. Os indivíduos não-binários ultrapassam os papéis sociais atribuídos aos gêneros, criando uma terceira identidade que foge do padrão "homem-mulher".</p>', 'multipla_escolha', 1, 'Cisgênero, Transgênero, Não-binário, Prefiro não dizer', 1);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, grid_rows, ordem) VALUES
(3, 'Q11', 'A empresa oferece oportunidades e tratamento igualitários para todos, proporcionando um ambiente de trabalho livre de preconceito e desigualdade, independente dos fatores:', 'grid', 1, 'Gênero, Idade, Cor ou raça, Religião, Orientação sexual, Condição física', 2);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(3, 'Q12', 'Independente da minha origem, idade, raça, experiências, personalidade, religião e orientação sexual, sou respeitado e acolhido pelo meu gestor e minha equipe de trabalho', 'escala', 1, 3),
(3, 'Q13', 'A empresa demonstra uma visão ampla e atrativa para todos, respeita as diferenças e valoriza a pluralidade', 'escala', 1, 4),
(3, 'Q14', 'A empresa trata de forma adequada situações que envolvem preconceito, discriminação ou condutas fora de sua cultura', 'escala', 1, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 4: CULTURA ORGANIZACIONAL
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(4, 'Q15', 'Me identifico com a Cultura Organizacional da Vizca', 'escala', 1, 1),
(4, 'Q16', 'Os valores propagados pela Vizca são realmente colocados em prática', 'escala', 1, 2),
(4, 'Q17', 'Me sinto pertencente à Vizca', 'escala', 1, 3),
(4, 'Q18', 'A Vizca é um bom lugar para se trabalhar', 'escala', 1, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 5: DESENVOLVIMENTO
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(5, 'Q19', 'A empresa proporciona condições de desenvolvimento para que eu tenha um aprendizado contínuo', 'escala', 1, 1),
(5, 'Q20', 'Estou satisfeito com os estímulos de desenvolvimento oferecidos pela empresa (Ex.: PDI e PDO).', 'escala', 1, 2),
(5, 'Q21', 'Tenho oportunidade de sugerir e negociar meu plano de desenvolvimento', 'escala', 1, 3),
(5, 'Q22', 'Tenho oportunidade de aplicar meus conhecimentos no meu trabalho', 'escala', 1, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 6: VALORIZAÇÃO E RECONHECIMENTO
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(6, 'Q23', 'Tenho oportunidade de desenvolvimento profissional na empresa', 'escala', 1, 1),
(6, 'Q24', 'Dentro do possível, tenho liberdade para fazer o meu trabalho da forma que considero melhor', 'escala', 1, 2),
(6, 'Q25', 'Meu potencial de realização profissional têm sido adequadamente aproveitado', 'escala', 1, 3),
(6, 'Q26', 'Tenho autonomia para propor melhorias na execução do meu trabalho', 'escala', 1, 4),
(6, 'Q27', 'Minhas ideias e sugestões são ouvidas', 'escala', 1, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 7: CRESCIMENTO PROFISSIONAL
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(7, 'Q28', 'A empresa proporciona espaço e estimula o crescimento profissional', 'escala', 1, 1),
(7, 'Q29', 'Tenho interesse em assumir novos desafios e responsabilidades na empresa', 'escala', 1, 2),
(7, 'Q30', 'Entendo quais são os requisitos necessários para ocupar outras posições na empresa', 'escala', 1, 3);

-- ============================================
-- PERGUNTAS - SEÇÃO 8: GESTÃO E LIDERANÇA
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(8, 'Q31', 'As orientações que a empresa fornece para realização do trabalho são claras e objetivas', 'escala', 1, 1),
(8, 'Q32', 'Recebo informações regulares sobre o meu desempenho', 'escala', 1, 2),
(8, 'Q33', 'Há espaço para que eu contribua com as tomadas de decisão do meu gestor ou responsável imediato', 'escala', 1, 3),
(8, 'Q34', 'Minhas entregas são reconhecidas pelo meu gestor', 'escala', 1, 4),
(8, 'Q35', 'Recebo suporte necessário para a realização do meu trabalho', 'escala', 1, 5),
(8, 'Q36', 'Me sinto à vontade para solicitar ou dar feedback ao meu gestor', 'escala', 1, 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 9: FUNÇÕES DESEMPENHADAS
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(9, 'Q37', 'Estou satisfeito com as funções que desempenho no meu dia a dia', 'escala', 1, 1),
(9, 'Q38', 'Entendo a importância das minhas atividades para os objetivos da organização', 'escala', 1, 2),
(9, 'Q39', 'Consigo cumprir minhas atividades de trabalho sem sobrecarga', 'escala', 1, 3),
(9, 'Q40', 'A empresa realiza ações de prevenção e controle em resposta a possíveis impactos relacionados à sobrecarga/demandas excessivas', 'escala', 1, 4),
(9, 'Q41', 'Tenho tempo suficiente para realizar minhas atividades', 'escala', 1, 5),
(9, 'Q42', 'Me sinto desafiado (positivamente) no meu trabalho', 'escala', 1, 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 10: RELACIONAMENTO EQUIPE
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(10, 'Q43', 'Me sinto confortável com minha equipe de trabalho', 'escala', 1, 1),
(10, 'Q44', 'Meu ambiente de trabalho é de cooperação e respeito', 'escala', 1, 2),
(10, 'Q45', 'No meu grupo de trabalho as pessoas se relacionam de forma harmoniosa', 'escala', 1, 3),
(10, 'Q46', 'Meus colegas estão comprometidos com os objetivos do trabalho', 'escala', 1, 4),
(10, 'Q47', 'Acredito que seja possível criar laços de amizade no ambiente de trabalho', 'escala', 1, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 11: COMUNICAÇÃO
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(11, 'Q48', 'A comunicação INSTITUCIONAL (política, códigos, objetivos, missão, visão, valores) é clara e objetiva', 'escala', 1, 1),
(11, 'Q49', 'A comunicação INTERNA (avisos, comunicados, mudanças, etc.) é clara e objetiva', 'escala', 1, 2),
(11, 'Q50', 'A comunicação de papéis e responsabilidades dentro da empresa é clara e objetiva', 'escala', 1, 3),
(11, 'Q51', 'A comunicação no dia a dia de trabalho é clara e facilita o entendimento mútuo.', 'escala', 1, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 12: REMUNERAÇÃO E BENEFÍCIOS
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(12, 'Q52', 'Estou satisfeito com minha remuneração', 'escala', 1, 1);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(12, 'Q53', 'Nos ajude a entender melhor a resposta anterior:', 'texto', 0, 2);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(12, 'Q54', 'Meu salário é justo para as atividades que desempenho', 'escala', 1, 3);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(12, 'Q55', 'Nos ajude a entender melhor a resposta anterior:', 'texto', 0, 4);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, descricao, tipo, obrigatoria, ordem) VALUES
(12, 'Q56', 'Estou satisfeito com os benefícios oferecidos pela empresa.', '<p class="mb-0"><small>São exemplos de benefícios: seguro de vida, wellhub/gympass, plr, VR/VA, convênio odontológico, convênio médico e VT.</small></p><p class="mb-0"><small><em>*Aplicável aos CLTs.</em></small></p>', 'escala', 1, 5);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(12, 'Q57', 'Nos ajude a entender melhor a resposta anterior:', 'texto', 0, 6);

-- ============================================
-- PERGUNTAS - SEÇÃO 13: INFRAESTRUTURA E FERRAMENTAS DE TRABALHO
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(13, 'Q58', 'Considero meu ambiente de trabalho seguro (organização, limpeza, revisões e manutenções em dia).', 'escala', 1, 1),
(13, 'Q59', 'Estou satisfeito com o conforto físico (temperatura, luminosidade)', 'escala', 1, 2),
(13, 'Q60', 'Os equipamentos fornecidos atendem as necessidades para o desenvolvimento da minha função', 'escala', 1, 3),
(13, 'Q61', 'A empresa disponibiliza equipamentos de qualidade. Exemplos de equipamentos: notebook, computador, teclado, mouse, suporte para o notebook)', 'escala', 1, 4),
(13, 'Q62', 'A empresa investe adequadamente em infraestrutura e tecnologia para apoiar o meu trabalho', 'escala', 1, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 14: MUDANÇAS
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(14, 'Q63', 'Como me sinto atualmente em relação às mudanças, tanto internas como externas (na empresa, nos clientes e no mercado)?', 'texto', 1, 1);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(14, 'Q64', 'Me sinto à vontade para compartilhar com o meu gestor, minhas preocupações em relação ao meu futuro na empresa', 'escala', 1, 2),
(14, 'Q65', 'A empresa está preocupada em garantir a estabilidade dos colaboradores', 'escala', 1, 3),
(14, 'Q66', 'A empresa está reagindo positivamente às mudanças, adotando novas estratégias e buscando novas oportunidades, para manter o seu desempenho e competitividade no mercado', 'escala', 1, 4);

-- ============================================
-- PERGUNTAS - SEÇÃO 15: GERAIS
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(15, 'Q67', 'O que mais te CONECTA à Vizca?', 'texto', 1, 1),
(15, 'Q68', 'O que mais te DESCONECTA da Vizca?', 'texto', 1, 2),
(15, 'Q69', 'Você identifica alguma situação ou incômodo presente?', 'paragrafo', 0, 3),
(15, 'Q70', 'Alguma ideia ou sugestão para a diretoria?', 'paragrafo', 0, 4),
(15, 'Q71', 'Existe algum ponto de atenção que você gostaria de comentar?', 'paragrafo', 0, 5);

-- ============================================
-- PERGUNTAS - SEÇÃO 16: ATUAÇÃO EM PROJETOS
-- ============================================
INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, opcoes, ordem) VALUES
(16, 'Q72', 'No ambiente onde atuo, o clima é satisfatório, contribuindo para o meu engajamento, motivação e o desempenho.', 'multipla_escolha', 1, 'Concordo Totalmente, Concordo, Não concordo e nem discordo, Discordo, Discordo Totalmente, N/A - Não aplicável', 1);

INSERT OR IGNORE INTO perguntas (secao_id, codigo, texto, tipo, obrigatoria, ordem) VALUES
(16, 'Q73', 'Se desejar, compartilhe os principais fatores que amparam sua resposta.', 'texto', 0, 2),
(16, 'Q74', 'Se desejar, compartilhe o nome do projeto que você atua', 'texto', 0, 3);
