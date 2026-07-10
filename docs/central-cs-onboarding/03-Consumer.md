---
date: 2026-06-24
tags: [doc, componente, worker, systemd, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[Cadencia]]"]
---
# Consumer — onboarding-consumer

## Identidade

- **Tipo:** worker Python (systemd service)
- **Stack:** Python 3.12 · cadencia-cli (subprocess) · consolidador_onboarding
- **Path:** `pd-framework/times/cs/workers/onboarding-consumer/consumer.py`
- **Status:** 🟢 produção (systemd `onboarding-consumer.service` na VPS Master)
- **Loop:** 30s

## O que é

Worker determinístico que lê a fila JSON do receiver, despacha o job pelo `tipo` e executa via `cadencia-cli` / `consolidador_onboarding`. Move jobs pra `processed/` (idempotente) ou `failed/`.

## Tipos de job

| `tipo` | Função | Origem |
|---|---|---|
| `consolidador` | `consolidador_onboarding.consolidar(slug, tenant_id, ...)` | Tally briefing |
| `crm_nota` | `cli contacts search` → `contacts note` | uso interno |
| `meeting` | resolve/cria contato + activity timeline (+ opp move se diagnóstico) + Slack se cancelado | Cal.com |
| `opp_move` | resolve contato pelo asaas_customer_id → opp pd-onboarding → stage_to | Asaas T-0 |

## Como funciona

1. Loop a cada 30s lê `ONBOARDING_QUEUE_DIR/*.json`.
2. `_processar_job(fpath)` → JSON → dispatch por `tipo`.
3. Sucesso → move pra `processed/`. Exception → `failed/`. Job não volta sozinho.
4. `dry_run = not APPLY` (gate consciente — default off).
5. Cancelamento Cal.com → notify Slack canal `rotina` (se `slack_notify` disponível).

## Gotchas

- **F2 — split nome:** `_resolver_contato` quebra "Maria Silva Costa" em `first="Maria"` + `last="Silva Costa"` antes de chamar `contacts create`.
- **opp_move pendente_mapeamento:** se contato não casa pelo `asaas_customer_id`, processa o job (não enfileira infinito) mas marca status (custom field é DEV-815/830/831).

## Env

| Var | Default | Pra quê |
|---|---|---|
| `ONBOARDING_QUEUE_DIR` | `<pd-root>/queue/onboarding` | fila compartilhada |
| `ONBOARDING_TENANT_ID` | `6bb2c1ba-...` | tenant PD |
| `ONBOARDING_APPLY` | _(off)_ | `1` = aplica; vazio = dry_run |
| `ONBOARDING_ALERTA_PARA` | _(off)_ | telefone Felipe |
| `ONBOARDING_SLACK_CANAL` | `rotina` | canal Slack para avisos internos |

## Don'ts

- Não rodar agente Claude tool-use junto.
- Não fazer push direto pra master sem rever (auto-deploy não, mas o systemd usa o `/opt/pd-framework/` ATUAL).
- Não esquecer `dry_run=True` quando o consolidador é chamado em teste.

## Relacionadas

- [[02-Receiver]] · [[04-Consolidador]] · [[01-Infra-Deploy]]
