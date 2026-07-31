# Stack Lara GCI-GO — VPS Dev

> **Cliente:** GCI-GO (Grupo GCI Goiás — 3 clínicas Sorria Goiás: Plano Piloto, Ceilândia, Central).
> **Status como consultoria PD:** ENCERRADO (pasta `times/produto/consultorias/encerrados/gci-go/`).
> **Status técnico:** RODANDO em modo degradado — 4 containers UP, processando reconcile dos 3 tenants em produção viva.
> **Última atualização real via compose:** desconhecida (compose file físico SUMIU com `userdel -r luiz`).

## O que é

Stack Python FastAPI + worker + Redis Streams + Postgres pgvector — chatbot WhatsApp de atendimento pros pacientes das 3 clínicas dentárias do Grupo GCI Goiás. Integrava com **middleware Ecuro** (API dental) pra consulta de agenda e agendamento automático, e com **GHL/GoHighLevel** como CRM do cliente.

**Não confundir com a Lara Cadencia** (produto SaaS, roda na VPS Master via Coolify, é a versão multi-tenant nova). São bases de código diferentes mesmo nome; documentação da Lara Cadencia em `times/produto/cadencia/docs/architecture/lara.md`.

## Contexto histórico (do PRD do cliente)

`times/produto/consultorias/encerrados/gci-go/00-PLANO.md` (2026-05-10):
> Após o sequestro da infra Hetzner pelo sócio Michael (07/05/2026) e o wipe nuclear (10/05/2026), o atendimento WhatsApp dos pacientes das 3 unidades ativas do Grupo GCI Goiás (Plano Piloto, Ceilândia, Central) ficou em vácuo operacional. (...) A reativação do atendimento de pacientes é a prioridade #1 agora.

Reativado em jun/26 pelo Luiz. Repositório fonte: [`Posicionamento-Digital/lara-ai`](https://github.com/Posicionamento-Digital/lara-ai) (confirmar). Deploy na VPS Dev via `docker compose` manual (fora do Coolify).

## Containers

Todos com `restart=unless-stopped`, subiram sozinhos após o reboot de 30/07 22h UTC.

### `lara-api` (FastAPI, exposta em `:8095`)

```
image: lara-lara-api (build local, não em registry — imagem existe só neste host)
cmd: sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8090}"
port: 8090 → host 8095
networks: lara-internal, pd-shared
status: Up 5h (healthy) — /health responde 200 a cada 15s
```

**ENV vars (mascarados):**
```
APP_ENV=development
PORT=8090
PUBLIC_BASE_URL=https://lara.cadencia.ia.br    ← exposta via cloudflared tunnel
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-5.4-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=***
EMBEDDING_DIM=1536
DATABASE_URL=postgresql+psycopg://lara:lara@lara-postgres:5432/lara
REDIS_URL=redis://lara-redis:6379/0
LARA_INTERNAL_API_KEY=***
ECURO_MIDDLEWARE_URL=http://ecuro-middleware:8080    ← container NÃO EXISTE (referência morta)
ECURO_MIDDLEWARE_API_KEY=***
ECURO_SMOKE_TENANT_ID=sorria-goias
ECURO_FLOW_ID=lara
ECURO_TIMEOUT_SECONDS=30
CONFIRMATION_QUEUE_URL=http://confirmation-queue-api:3000    ← container NÃO EXISTE
GHL_API_TOKEN=***
GHL_API_VERSION=2021-04-15
GHL_WEBHOOK_SECRET=***
LOG_LEVEL=INFO
DB_ECHO=false
```

### `lara-worker` (Python worker, sem porta exposta)

```
image: lara-lara-worker (build local)
cmd: python -m app.worker
networks: lara-internal, pd-shared
```

ENV = mesmo do `lara-api` + `LARA_PROCESS_LABEL=worker`.

**Logs ao vivo (2026-07-31):**
- `worker.health` a cada 10s (heartbeats: handoff, dispatch, confirm, metrics, prune, inbound, reconcile, recovery — todos com age < 1min exceto `prune` que passa dias sem rodar)
- `reconcile.tenant_done` pros 3 tenants a cada ciclo (a cada ~5min)
- Nenhuma mensagem de erro visível → modo reconcile só, sem tráfego de webhook real

### `lara-postgres` (pgvector)

```
image: pgvector/pgvector:pg16
volume: /var/lib/docker/volumes/lara-postgres-data/_data → /var/lib/postgresql/data
network: lara-internal (isolada)
```

**ENV:**
```
POSTGRES_USER=lara
POSTGRES_PASSWORD=lara         ← default weak (aceitável — network isolada, não exposta)
POSTGRES_DB=lara
PGDATA=/var/lib/postgresql/data/pgdata
```

Health: healthy (via `pg_isready` do image default).

### `lara-redis` (fila + cache)

```
image: redis:7-alpine
cmd: redis-server --appendonly yes --appendfsync everysec
volume: /var/lib/docker/volumes/lara-redis-data/_data → /data
network: lara-internal
```

Sem AUTH (network isolada). AOF persistence habilitado (`appendonly yes`).

## Modo degradado — o que quebrou

**Duas dependências de docker DNS morreram:**

1. `ecuro-middleware:8080` — worker chama pra consulta/mutação de agenda dental (Ecuro API). Container não existe na VPS. Efeito: qualquer skill que precise validar/reservar horário no consultório falha.
2. `confirmation-queue-api:3000` — worker chama pra fila de confirmação (era serviço Node? não confirmado). Container não existe.

**O que ainda funciona:**
- Webhook Evolution GO (externo, hospedado fora dessa VPS) chega em `lara.cadencia.ia.br` → tunnel → `lara-api:8095` → enfileira em `lara-redis` → `lara-worker` consome → agent decide resposta via OpenRouter/gpt-5.4-mini → grava em `lara-postgres` → chama Evolution GO pra responder no WhatsApp.
- Reconcile continua rodando (leitura das mensagens armazenadas, sem lateral externo).

**O que quebrou silenciosamente:**
- Fluxo de agendamento (o valor de negócio principal — "Lara agenda no eCuro" do PRD).
- Confirmação automática (já era fora de escopo pelo PRD, mas o env aponta pra `confirmation-queue-api` inexistente).

## 3 tenants Sorria Goiás processando

Vistos nos logs do worker:
| Slug | Tenant ID (interno da Lara) |
|---|---|
| `sorria-goias-plano-piloto` | `0964f213-bbd6-4f3e-bd13-e186565a5f68` |
| `sorria-goias-ceilandia`    | `596f3659-25fb-4f94-a8ce-cb78083aa326` |
| `sorria-goias-central`      | `82bc379f-1b7d-4cfd-87ef-52532f372e7f` |

**NÃO existem no Supabase Cadencia** (`elefbabxkaigusjiiflu`) — são tenants isolados no Postgres local (`lara-postgres`). Base de dados 100% independente do Cadencia.

## Volume de dados

`lara-postgres-data` (não medido — provável 100MB-1GB dado 3 tenants + ~2 meses de operação).
`lara-redis-data` (~MB, filas curtas).

Para backup: `docker exec lara-postgres pg_dump -U lara lara > backup.sql` (rodar como felipe via sudo).

## Compose file — RECONSTITUÍDO

O compose original em `/home/luiz/projetos/gci-go/lara/docker-compose.yml` **SUMIU** com o `userdel -r luiz` (30/07). Reconstituído a partir de `docker inspect`:

```yaml
# Reconstituído em 2026-07-31 a partir de docker inspect
# Original vivia em /home/luiz/projetos/gci-go/lara/docker-compose.yml
name: lara

services:
  lara-api:
    image: lara-lara-api     # build local — imagem existe só neste host
    restart: unless-stopped
    ports:
      - "8095:8090"
    depends_on:
      lara-postgres:
        condition: service_healthy
      lara-redis:
        condition: service_started
    networks:
      - lara-internal
      - pd-shared
    environment:
      APP_ENV: development
      PORT: "8090"
      PUBLIC_BASE_URL: https://lara.cadencia.ia.br
      LLM_PROVIDER: openrouter
      LLM_MODEL: openai/gpt-5.4-mini
      OPENROUTER_BASE_URL: https://openrouter.ai/api/v1
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
      EMBEDDING_DIM: "1536"
      DATABASE_URL: postgresql+psycopg://lara:lara@lara-postgres:5432/lara
      REDIS_URL: redis://lara-redis:6379/0
      LARA_INTERNAL_API_KEY: ${LARA_INTERNAL_API_KEY}
      ECURO_MIDDLEWARE_URL: http://ecuro-middleware:8080
      ECURO_MIDDLEWARE_API_KEY: ${ECURO_MIDDLEWARE_API_KEY}
      ECURO_SMOKE_TENANT_ID: sorria-goias
      ECURO_FLOW_ID: lara
      ECURO_TIMEOUT_SECONDS: "30"
      CONFIRMATION_QUEUE_URL: http://confirmation-queue-api:3000
      GHL_API_TOKEN: ${GHL_API_TOKEN}
      GHL_API_VERSION: "2021-04-15"
      GHL_WEBHOOK_SECRET: ${GHL_WEBHOOK_SECRET}
      LOG_LEVEL: INFO
      DB_ECHO: "false"

  lara-worker:
    image: lara-lara-worker
    restart: unless-stopped
    command: python -m app.worker
    depends_on:
      lara-redis:
        condition: service_started
      lara-postgres:
        condition: service_healthy
    networks:
      - lara-internal
      - pd-shared
    environment:
      # (mesmo do lara-api) +
      LARA_PROCESS_LABEL: worker

  lara-postgres:
    image: pgvector/pgvector:pg16
    restart: unless-stopped
    environment:
      POSTGRES_USER: lara
      POSTGRES_PASSWORD: lara
      POSTGRES_DB: lara
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - lara-postgres-data:/var/lib/postgresql/data
    networks:
      - lara-internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lara"]
      interval: 10s

  lara-redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --appendfsync everysec
    volumes:
      - lara-redis-data:/data
    networks:
      - lara-internal

networks:
  lara-internal:
    external: true          # já criado
  pd-shared:
    external: true

volumes:
  lara-postgres-data:
    external: true          # já existe
  lara-redis-data:
    external: true
```

**Onde salvar novo compose:** recomendo `/home/felipe/compose/lara-gci-go/docker-compose.yml`. Salvar também os secrets num `.env` sibling (buscados do 1P). Detalhe do procedimento em [`runbook-recuperar-compose.md`](runbook-recuperar-compose.md).

---

## API — 53 rotas (via OpenAPI `/openapi.json`)

Endpoint público único: `POST /webhooks/ghl` (webhook do GHL/GoHighLevel). Painel admin protegido por login + 2FA opcional.

### Rotas principais

**Público:**
- `GET /health` — liveness (Docker healthcheck)
- `POST /webhooks/ghl` — inbound do GHL (conversa nova / mensagem)
- `GET /media/outbound/{filename}` — arquivos de mídia enviados
- `POST /internal/smoke-tests/ecuro` — sanity check integração dental

**Admin auth (`/internal/admin`):** `login`, `logout`, `change-password`, `me`, `me/permissions`, `me/2fa/{setup,enable,disable}`

**Admin tenants (CRUD):** `GET|POST /tenants`, `GET|PUT|DELETE /tenants/{slug}`, `/tenants/{slug}/reveal-secret` (mostra webhook token), `POST /tenants/{slug}/test` (envia mensagem teste)

**Métricas por tenant:** `/tenants/{slug}/metrics{,/appointments,/handoffs,/failures,/tool-errors,/latency,/guardrails}`

**Conversas + handoff humano:** `/tenants/{slug}/conversations`, `/conversations/{id}/{timeline,profile,head,media}`, `POST /conversations/{id}/{send,send-audio,pause,resume}`, `GET /pause-state`, `DELETE /conversations/{id}`

**Usuários operadores:** `GET|POST /users`, `POST /users/{id}/{password,active}`, `PUT /users/{id}/permissions`

**Observabilidade:** `/logs`, `/logs/{trace,stream}`, `/audit`, `/workers`, `/queues`, `/integrations/health`, `/metrics/global`, `/openrouter/{models,refresh}`

## Estrutura do código (`/app/app/`)

```
adapters/        # Evolution/GHL adapters (não inspecionado)
admin/           # rotas + auth + 2FA
agent/           # o cérebro
  graph.py, guardrails.py, llm.py, prompt.py, runtime.py
  splitter.py, tools.py, whatsapp_format.py, availability_filter.py
core/            # config, db session
db/              # SQLAlchemy models + Alembic migrations
handoff.py       # lógica handoff humano
inbound/         # webhook handlers (routes.py)
internal/        # smoke tests
main.py          # FastAPI app entrypoint
media/           # upload/download mídia (routes.py)
memory/          # memória do agent (contact_facts, kb_chunks)
observability/   # logs + traces + audit
outbound/        # envio de mensagens
tools/           # ⚠️ SÓ tem gateway.py (wrapper HTTP genérico pra Ecuro middleware — que sumiu)
reconcile.py     # reconciliador batch (roda no worker — reconcile.tenant_done nos logs)
worker.py        # entrypoint `python -m app.worker` (fila Redis Streams)
```

**Insight crítico:** a única tool disponível pro agent hoje é `tools/gateway.py` → chama `http://ecuro-middleware:8080` (**container não existe mais**). Logo: agent responde texto, mas **não consegue mais consultar/marcar agenda no Ecuro**. É o "modo degradado" que o cliente sentiria se voltasse a usar.

## Schema Postgres (`lara-postgres`, DB `lara`) — 34 tabelas, Alembic `0009`

**Core:** `tenants` (3), `admin_users`+`admin_memberships`+`admin_user_permissions`+`admin_audit_log`, `channels`, `conversations` (369), `conversation_turns`, `messages` (3046), `raw_events`, `contact_facts`, `outbound_messages`.

**Agent/IA:** `kb_chunks` (RAG), `tool_calls`, `guardrail_events`.

**Observabilidade:** `log_events_YYYYMMDD` particionadas por dia (rolling window visível `20260527..20260731`).

**Sem tabela `appointments` local** — agendamento gravava no Ecuro externo.

## Tráfego real — DADOS DE HOJE (2026-07-31)

```
sorria-goias-central       285 conversations,  0 msgs últimas 24h
sorria-goias-plano-piloto   84 conversations,  0 msgs últimas 24h
sorria-goias-ceilandia       0 conversations aparentes

Mensagens nos últimos 7 dias: 0
```

**Cliente NÃO usa mais ativamente.** Os 369 conversations + 3046 msgs são acumulado antigo (últimas mensagens antes de 2026-07-24). Só o `reconcile` batch roda passivo (por isso os logs do worker mostram só `reconcile.tenant_done`).

**Conclusão operacional:** desligar a stack agora **não afeta cliente vivo** — só perde histórico se não fizer backup.

## Como operar

### Health / observabilidade
```bash
sudo docker exec lara-api curl -s http://localhost:8090/health
sudo docker logs lara-api --tail 50
sudo docker logs lara-worker --tail 50
sudo docker exec lara-redis redis-cli DBSIZE
sudo docker exec lara-postgres psql -U lara -d lara -c \
  "SELECT t.slug, COUNT(DISTINCT c.id) conv, COUNT(m.id) msgs
   FROM conversations c JOIN tenants t ON t.id=c.tenant_id
   LEFT JOIN messages m ON m.conversation_id=c.id
   GROUP BY t.slug"
```

### Painel admin (JSON — sem UI web separada)
```bash
# Ver admins
sudo docker exec lara-postgres psql -U lara -d lara -c "SELECT email, active FROM admin_users"

# Login
curl -X POST http://localhost:8095/internal/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"...","password":"..."}'
```

### Backup Postgres (crítico se manter)
```bash
sudo docker exec lara-postgres pg_dump -U lara lara \
  | gzip > /root/backup-lara-$(date -u +%Y%m%dT%H%M).sql.gz
scp /root/backup-lara-*.sql.gz master@72.60.4.71:/backups/vps-dev/
```

### Restart limpo
```bash
sudo docker restart lara-worker lara-api    # postgres/redis mantém state
```

### Parar sem perder dados
```bash
sudo docker stop lara-worker lara-api lara-redis lara-postgres
# Volumes preservados. Sobe reverso com `docker start`.
```

### Deletar tudo (após backup + confirmação Felipe)
```bash
sudo docker rm -f lara-worker lara-api lara-redis lara-postgres
sudo docker volume rm lara-postgres-data lara-redis-data
sudo docker network rm lara-internal
# + remover DNS lara.cadencia.ia.br + endpoint no Cloudflare tunnel
```

## Decisões a tomar sobre esse stack

1. **Manter?** Cliente encerrado como consultoria mas 3 tenants ainda processam. Descoberta 30/07: Felipe precisa dizer se continuar hospedando (é serviço zumbi de courtesia OU cliente ainda paga manutenção).
2. **Restaurar `ecuro-middleware` + `confirmation-queue-api`?** Só faz sentido se decidir manter + reativar agendamento automático. Provavelmente ambos vivem em repos separados (`Posicionamento-Digital/ecuro-mcp` + algo pra queue).
3. **Migrar pra Master (Coolify)?** Se manter longo prazo, faz sentido — VPS Dev era pra ser interativo, não produção. Requer rebuild das imagens (que só existem local) e provisionamento de secrets no Coolify.
4. **Desligar limpo?** `docker compose down` + backup do postgres/redis + comunicar cliente + deletar volumes + remover DNS `lara.cadencia.ia.br`.

## Refs

- Projeto encerrado: `times/produto/consultorias/encerrados/gci-go/`
  - `00-PLANO.md` — plano de reativação pós wipe nuclear (2026-05-10)
  - `PRD.md` — RF-1 a RF-31 (requisitos funcionais)
  - `epics/EPIC-1` a `EPIC-5` — arquitetura implementada
  - `arquitetura/referencias-luiz/` — código exemplo Central bot
  - `Prompts agentes/Prompt_LaraCentral.txt` — system prompt da Lara
  - `memory/STATE.md` — status L1-L3 (última atualização 2026-06-01)
- Middleware Ecuro (referência): `times/produto/consultorias/encerrados/gci-go/arquitetura/mcp_ecuro_tools.json`
- Repo GitHub: `Posicionamento-Digital/lara-ai` (Coolify app "Lara v2" existe mas exited há tempo — código-base é ancestral desta stack, provavelmente drift enorme)
- Doc do webhook Evolution GO: `times/produto/cadencia/docs/features/lara/evolution-go-webhook-map.md` (mapeamento do payload whatsmeow, útil aqui também)
