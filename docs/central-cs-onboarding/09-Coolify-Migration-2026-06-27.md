---
date: 2026-06-27
tags: [documentacao, projeto, infra]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
## Identidade
- **Tipo:** infra · webhook receiver
- **Stack:** Python 3.13 · FastAPI · Docker
- **Repo:** `Posicionamento-Digital/onboarding-webhooks`
- **Deploy:** Coolify-managed na VPS Master (UUID `dl5qtso0klt2z5yzwkixbgxa`)
- **Domínio:** https://onboarding.cadencia.ia.br
- **Status:** ativo

## O que é
Receivers de webhook (Tally, Cal.com, Asaas) do projeto Automação do Onboarding CS. Determinístico (sem agente tool-use). Valida `X-Webhook-Secret`, despacha por handler, enfileira jobs em `/queue` (volume bind compartilhado com `onboarding-consumer.service` no host).

## Para que serve
Fechar o loop `evento externo → consumer determinístico → CRM/Linear/WhatsApp` sem o agente Claude no caminho crítico. Cliente preenche form Tally / agenda no Cal.com / paga 1ª parcela no Asaas → receiver enfileira → consumer atua.

## Como funciona

```
Tally/Cal.com/Asaas
  → POST onboarding.cadencia.ia.br/<source> + X-Webhook-Secret
    → handler (app/handlers/<source>.py) valida + extrai payload
      → integration.enfileirar_* grava JSON em /queue (volume bind)
        → onboarding-consumer.service (systemd no host) lê fila
          → despacha por job.tipo → CRM Cadencia + Linear + WhatsApp
```

**Handlers ativos:**
- `tally.py` — 2 fluxos: form de briefing (DEV-808) + form de stakeholders (DEV-903, detecção por whitelist de formId ou heurística "papel + valor canônico")
- `calcom.py` — sync Cal.com → CRM com extração tolerante v1/v2 via helper `_g(d, *paths)` (DEV-904)
- `asaas.py` — 1ª parcela = T-0 (DEV-810)

## Migração para Coolify (2026-06-27, DEV-906)

Antes: `docker run` manual em `/opt/onboarding-webhooks/` na VPS Master (DEV-837).
Depois: Coolify-managed com auto-deploy on push em `main`.

**Por quê:** drift entre código no repo e código rodando, env vars fora do 1Password sem audit, qualquer fix exigia SSH manual. Coolify resolve os 3 + ainda dá painel web pra logs/restart/rollback.

**Stack Coolify:**
- App UUID: `dl5qtso0klt2z5yzwkixbgxa`
- Projeto: Cadencia (`wbaqjeeyabmiy0gylk8ywutf`)
- GitHub App: `coolify-vpsmaster` (auto-deploy)
- Volume bind: `/var/onboarding-queue:/queue` (compartilhado com consumer systemd)

## Quickstart

```bash
ssh master "docker ps --filter name=dl5qtso0klt2z5yzwkixbgxa --format '{{.Status}}'"
curl -s -o /dev/null -w "%{http_code}\n" https://onboarding.cadencia.ia.br/tally
# Esperado: 405 (GET não permitido, POST exige secret)

git push origin main  # → Coolify auto-deploy
```

## Decisões (ADRs)
- Volume bind em vez de fila externa (Redis/RabbitMQ) — receiver e consumer no mesmo host, zero overhead
- Auto-deploy on push como default — evita drift
- Cadencia é projeto Coolify padrão pra todo app PD novo

Detalhe: `pd-framework/_core/COOLIFY-APPS.md`

## Don'ts
- **Nunca** commitar `.env` real. Env vars vivem só no Coolify panel.
- **Nunca** alterar config no painel Coolify sem registrar em `_core/COOLIFY-APPS.md`.
- **Nunca** rodar `docker run` manual de novo — o app é gerenciado pelo Coolify.
- **Nunca** mudar o volume bind sem coordenar com `onboarding-consumer.service` (quebra a fila).

## Troubleshooting

- **`GET /tally` retorna 200 ou outro código ≠ 405** → container caiu. Checar `docker logs <container>` no Master.
- **`POST /tally` com secret retorna 401** → `WEBHOOK_SECRET` no Coolify diverge do Tally. Comparar via painel.
- **Job não aparece em `/queue`** → permissão do volume bind. Container precisa de write em `/queue`.

## Histórico
- 2026-06-27 — Migrado pra Coolify (DEV-906) + handler stakeholders (DEV-903) + tolerância v1/v2 Cal.com (DEV-904). Commit `908ae89`.
- 2026-06-24 — Consumer separado (`onboarding-consumer.service`) na VPS Master.
- 2026-05 — Esqueleto inicial (DEV-807).

## Notas Relacionadas
[[Projetos/Central CS Onboarding/Docs/00-Visao-Geral]] · [[Projetos/Central CS Onboarding/Docs/01-Infra-Deploy]] · [[Projetos/Central CS Onboarding/Docs/02-Receiver]] · [[Projetos/Migracao-VPS-Coolify/Brief]]
