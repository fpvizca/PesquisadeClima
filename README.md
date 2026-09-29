# Pesquisa de Clima VIZCA

Sistema interno de pesquisa de clima organizacional. Flask + SQLite.

## Requisitos

- Python 3.11+
- Acesso a rede ao Ollama (para análise por IA)
- Acesso a rede à API de autenticação `https://relats.vizca.com.br`

## Instalação rápida (Linux)

```bash
cp .env.example .env
nano .env                      # defina o SECRET_KEY
chmod +x iniciar.sh
./iniciar.sh
```

O script cria o ambiente virtual, instala as dependências, aplica as migrations
e sobe o servidor via gunicorn.

Gerar um SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Instalação rápida (Windows)

```bat
executar.bat
```

## Docker

```bash
cp .env.example .env           # defina o SECRET_KEY
docker compose up -d --build
```

Acesse em `http://localhost:8120`.

O banco fica no volume `clima_data` (montado em `/app/data`), então os dados
persistem mesmo reconstruindo a imagem.

## Primeira configuração

O `seed.sql` cria **apenas 1 usuário local**:

| Login  | Senha     | Papel        |
|--------|-----------|--------------|
| admin  | admin123  | administrador|

**Troque essa senha em "Trocar Senha" logo após o primeiro acesso.**

Todos os demais colaboradores entram pela API externa e são criados
automatically at first access — they have no local password.

## Produção

## Variáveis de ambiente

| Variável        | Padrão                            | Descrição                                  |
|-----------------|-----------------------------------|--------------------------------------------|
| `SECRET_KEY`    | —                                 | **Obrigatório em produção.** Chave da sessão |
| `DEBUG`         | `false`                           | Nunca use `true` em produção                |
| `PORT`          | `5005`                            | Porta da aplicação                         |
| `HOST`          | `127.0.0.1`                       | Use `0.0.0.0` para expor na rede           |
| `SESSION_MINUTES` | `20`                            | Duração da sessão                          |
| `API_BASE`      | `https://relats.vizca.com.br`     | API de autenticação                        |
| `OLLAMA_BASE`   | `http://192.168.170.12:11434`     | Endereço do Ollama                         |
| `OLLAMA_MODEL`  | `ministral-3:8b`                  | Modelo usado na análise por IA              |
| `ANO_PESQUISA`  | ano do ciclo ativo ou ano atual   | Ano citado na mensagem de bloqueio         |
| `DATABASE_PATH` | `./clima.db`                      | Caminho do banco SQLite                    |

## Banco de dados e migrations

```bash
python migrar.py
```

O migrador é **idempotente** — pode rodar quantas vezes quiser. Ele:

1. Aplica `schema.sql` (todas as `CREATE TABLE IF NOT EXISTS`)
2. Aplica `seed.sql` apenas se a tabela `usuarios` estiver vazia
3. Adiciona colunas novas (`ciclos.titulo`, `ciclos.texto_abertura`)
4. Cria a tabela `usuarios_bloqueados` e popula a lista de bloqueados

### Por que `migrate_v2.sql` e `migrate_v3.sql` não são executados

Esses dois arquivos são históricos e **contraditórios entre si**: o `v3` remove
a coluna `respostas.usuario_id`, que o schema atual utiliza. Bancos novos já
nascem corretos pelo `schema.sql`; bancos existentes já têm `v2` e `v3`
aplicadas. Rode-os apenas para bancos muito antigos, manualmente e com backup.

## Autenticação

O login tenta primeiro a API externa (`relats.vizca.com.br`). Se ela responder,
o usuário é criado/atualizado localmente e a sessão é iniciada. Se a API estiver
indisponível, o sistema tenta o login local — mas **apenas o `admin` tem senha
local**, então uma queda da API impede o acesso de todos os colaboradores até
que ela volte. A tela de login avisa quando detecta esse cenário.

## Anonimato

O ciclo de vida de uma resposta é:

1. **Enquanto o ciclo está aberto** — `respostas.usuario_id` guarda quem
   respondeu, para que o colaborador possa consultar e editar as próprias
   respostas. É um vínculo **pseudonimizado**, não anônimo.
2. **Ao anonimizar o ciclo** — o administrador clica no botão de escudo em
   *Gerenciar Ciclos*. Todas as respostas do ciclo têm o `usuario_id` definido
   como `NULL` e `ciclos.anonimizado_em` é gravado. O vínculo é removido de
   forma definitiva e **não pode ser desfeito**.

Depois da anonimização as respostas não podem mais ser editadas, e
`COUNT(DISTINCT usuario_id)` passa a retornar zero — por isso as telas de
resultados exibem "Respondentes: 0" nesse estado.

Para quem tem acesso ao arquivo `clima.db`: a operação zera o vínculo de todas
as respostas do ciclo, portanto um `JOIN respostas → usuarios` deixa de
reconstruir quem respondeu o quê.

## Logins bloqueados

Colaboradores com menos de 3 meses de empresa recebem a mensagem:

> A pesquisa de clima VIZCA {ano} é direcionada para colaboradores com mais de
> 3 meses de empresa. Os colaboradores que não estiverem nesta situação poderão
> participar da próxima pesquisa.

A lista fica na tabela `usuarios_bloqueados` e pode ser gerenciada em
**Logins Bloqueados** no menu lateral (admin). O bloqueio é aplicado no login e
em sessões já ativas. A comparação do login ignora maiúsculas/minúsculas.

## Produção

Antes de publicar:

- [ ] `DEBUG=false`
- [ ] `SECRET_KEY` forte e única (trocar a cada implantação invalida as sessões)
- [ ] Senha do `admin` alterada em "Trocar Senha"
- [ ] HTTPS na frente da aplicação (Nginx ou proxy do corporate)
- [ ] Backup do `clima.db`

### systemd

```ini
[Unit]
Description=Pesquisa de Clima Vizca
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pesquisa-clima
EnvironmentFile=/opt/pesquisa-clima/.env
ExecStart=/opt/pesquisa-clima/iniciar.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx

```nginx
server {
    listen 80;
    server_name clima.vizca.com.br;

    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # A exportação Word chama o Ollama e pode demorar
        proxy_read_timeout 300s;
    }
}
```

## Notas técnicas

- A aplicação avisa no startup quando `SECRET_KEY` está ausente, curta ou igual
  ao padrão de desenvolvimento. Nesse caso as sessões ficam inseguras.
- A exportação Word chama o Ollama para cada seção e cada pergunta, então pode
  demorar alguns minutos com muitas respostas. O `--timeout 180` do gunicorn
  existe para cobrir esse caso.
- `usuario_id` em `respostas` é usado apenas para permitir que o colaborador
  edite as próprias respostas. Nunca é exposto em telas de admin ou exportações.
