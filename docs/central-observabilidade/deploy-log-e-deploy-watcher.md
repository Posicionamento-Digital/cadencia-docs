---
date: 2026-07-04
tags: [doc, documentacao, projeto, observabilidade]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]"]
---
# deploy_log — registro unificado de deploys (DEV-1160)

## TL;DR
Toda plataforma que deploya (Vercel, Coolify, Supabase) grava 1 registro na tabela `deploys` do Supabase Hub PD e posta no Slack `#deploys` — idempotente por `deployment_id`, consultável de qualquer ambiente via CLI.

## Identidade
- **Tipo:** lib + CLI (Python, stdlib)
- **Path:** `_shared/deploy_log.py`
- **Sink:** tabela `deploys` @ Supabase Hub PD (`himbzxljoqaocvkiyjvx`)
- **Slack:** canal `#deploys` (`C0BEZQD7YQK`, roteado por `_shared/slack_notify.py`)
- **Dependências:** `_shared/supabase_client.py` (Management API) · `_shared/slack_notify.py`
- **Status:** ativo (04/07/2026)

## Como funciona
1. `record(...)` faz upsert em **1 query** (CTE lê o status anterior — a Management API tem throttle ~60 req/min) com `on conflict (deployment_id)`.
2. Slack só em **novidade ou transição pra status terminal** (READY/ERROR/FAILED/CANCELED/FINISHED) — rodada de poller sem mudança é silenciosa.
3. `record_bulk(events)` insere N deploys numa query única, **sem Slack** — é o caminho do backfill (o poller descobre histórico antigo na 1ª rodada; 92 eventos = 1 query, zero spam).

## Quickstart
```bash
python _shared/deploy_log.py record --platform supabase --system cadencia-app \
  --deployment-id "mig-20260704-audit" --status READY
python _shared/deploy_log.py list --system cadencia-app --last 10
```

## Quando usar / NÃO usar
- **Usar:** qualquer ponto de disparo de deploy sem webhook (ex.: skills que rodam `supabase db push`/`functions deploy` devem chamar `record --platform supabase` ao concluir).
- **NÃO usar:** pra Vercel/Coolify manualmente — o poller `times/infra/workers/deploy_watcher.py` já cobre.

## Don'ts
- NÃO reutilizar `_q()` (escape manual de SQL) fora deste módulo — a Management API não aceita query parametrizada; a limitação está contida aqui de propósito.
- NÃO postar no Slack direto — passe pelo `record()` (é ele que garante dedup webhook×poller).

## Troubleshooting
- **`erro da API: ThrottlerException`** → Management API rate-limitada; use `record_bulk` pra lote, nunca loop de `record`.
- **Slack não postou mas a linha existe** → por design (evento antigo ou sem transição terminal).

## Histórico
- 2026-07-04 — criado (DEV-1160), validado com 92 deploys reais (6 Vercel + 86 Coolify)


---

# deploy_watcher — poller de deploys Vercel + Coolify (DEV-1160)

## TL;DR
Cron determinístico na VPS Master (*/10min) que consulta as APIs do Vercel e do Coolify e entrega cada deploy pro `_shared/deploy_log.py` (tabela `deploys` + Slack `#deploys`).

## Identidade
- **Tipo:** worker/cron (Python stdlib)
- **Path:** `times/infra/workers/deploy_watcher.py` · roda em `/opt/pd-framework/` (Master, user master)
- **Cron:** `*/10 * * * *` (crontab do master), sourceando `~/.config/pd/op.env`
- **Estado:** `~/.deploy-watcher/state.json` (cursor Vercel; recua 30min pra pegar BUILDING→READY)
- **Secrets:** `VERCEL_TOKEN` + `COOLIFY_API_TOKEN` via `_shared/secrets` (mapa `_core/SECRETS-1P-MAP.json`)
- **Vigiado por:** health check (`jobs.json`, mtime de `~/logs/deploy-watcher.log`)

## Por que poller e não webhook
Webhook de deploy do Vercel é feature **Pro** (conta é Hobby — incidente 27/06). O poller cobre Vercel e Coolify pelo mesmo caminho. Deploys do Supabase não têm API de histórico — são registrados no ponto de disparo (`deploy_log.py record`).

## Como funciona
1. Vercel: `GET /v6/deployments?since=<cursor>` (todos os projetos da conta).
2. Coolify: `GET /deployments/applications/{uuid}` por app (últimos 10).
3. Evento **recente (≤45min)** → `record()` individual com Slack; **antigo** → `record_bulk()` silencioso (anti-spam de backfill).

## Quickstart
```bash
# local (Windows) — Coolify pela FQDN pública
COOLIFY_BASE=https://coolify.cadencia.ia.br/api/v1 python times/infra/workers/deploy_watcher.py --dry-run
```

## Don'ts
- NÃO rodar 2 instâncias (o dedup segura duplicata na tabela, mas o Slack pode duplicar na janela recente).

## Troubleshooting
- **`vercel: poll falhou 403`** → token rotacionado; atualizar item `Vercel - api - cli` (vault Hosts).
- **Coolify vazio** → API local `localhost:8000` só existe na Master; fora dela exporte `COOLIFY_BASE`.

## Histórico
- 2026-07-04 — criado (DEV-1160); ativação guardada por existência do arquivo (pull das 06:00)


## Notas Relacionadas
[[self-test-suite]] · [[hostinger-watcher]]
