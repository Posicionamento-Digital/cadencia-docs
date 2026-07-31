# Stack Hermes Agent — VPS Dev

> **Origem:** third-party open-source ([NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)).
> **Escopo:** laboratório pessoal do Felipe (não é serviço da PD, não atende cliente).
> **Estado atual:** compose file existe em `/home/felipe/.hermes/hermes-agent/docker-compose.yml`, container `hermes` **não está rodando** agora.

## O que é

**Hermes Agent** = agente de IA self-improving (loop de auto-aprendizado) da **Nous Research**. Do README oficial:

> The self-improving AI agent built by Nous Research. It's the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions. Run it on a $5 VPS, a GPU cluster, or serverless infrastructure that costs nearly nothing when idle. It's not tied to your laptop — talk to it from Telegram while it works on a cloud VM.

Container único (`hermes`), rodaria com `network_mode: host` (usa portas do host direto). Dashboard local em `127.0.0.1` que guarda API keys — instruído no compose a NÃO expor `--host 0.0.0.0` sem auth.

## Config atual (compose existente)

Arquivo: `/home/felipe/.hermes/hermes-agent/docker-compose.yml`

```yaml
services:
  gateway:
    build: .
    image: hermes-agent
    container_name: hermes
    restart: unless-stopped
    network_mode: host
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_UID=${HERMES_UID:-10000}
      - HERMES_GID=${HERMES_GID:-10000}
      # (Teams, Google Chat, API server — todos comentados/opt-in)
```

Uso instruído: `HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d`.

## Estado real

```
$ docker ps -a | grep hermes
(nada — container não existe hoje)
```

Compose file presente + repo clonado, mas nunca subido nesta VPS OU subido e removido depois. `.hermes/` no home do Felipe pode conter estado de rodagens anteriores.

## Por que existe aqui

Não achei doc formal do porquê Felipe tem isso. Provável hipótese (não confirmada): experimento pessoal com agente self-improving pra comparar com o pattern de Claude Code + Codex do Motor PD. Zero ligação com produtos Cadencia.

## Decisões a tomar

1. **Se não usa** — remover repo (`rm -rf /home/felipe/.hermes/hermes-agent/`) + limpar `~/.hermes/` (dados). Libera ~poucos MB.
2. **Se pretende usar** — subir com `HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d` no dir do compose. Cuidar do `network_mode: host` — usa portas do host, pode conflitar com o que já roda (`:8085`, `:8095`, `:22`, etc). Verificar `netstat -tlnp` antes de subir pra saber quais portas hermes tenta abrir.

## Riscos

- **`network_mode: host`** — se subir, tem acesso direto a toda porta local (loopback + interfaces). Zero isolamento de rede — mais permissivo que rede bridge default.
- **Dashboard armazena API keys** — se acidentalmente exposto com `--host 0.0.0.0` sem auth, vaza credenciais LLM.
- **Volume `~/.hermes:/opt/data`** — se apagar `~/.hermes/` na correria, perde todo o estado aprendido.

## Refs

- Repo: https://github.com/NousResearch/hermes-agent
- Doc oficial: https://hermes-agent.nousresearch.com/docs/
- Local: `/home/felipe/.hermes/hermes-agent/` (compose) + `/home/felipe/.hermes/` (data volume)
