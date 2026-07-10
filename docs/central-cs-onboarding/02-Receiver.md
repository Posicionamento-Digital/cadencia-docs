---
date: 2026-06-24
tags: [doc, componente, webhook, fastapi, docker, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[Cadencia]]"]
---
# Receiver — onboarding-webhooks

## Identidade

- **Tipo:** FastAPI receiver (containerizado)
- **Stack:** Python 3.12 · FastAPI + uvicorn · curl subprocess (dispatch)
- **Path:** `_repos/onboarding-webhooks/`
- **Repo:** `Posicionamento-Digital/onboarding-webhooks`
- **Status:** 🟢 produção (VPS Master)
- **Porta:** 9400

## O que é

Container Docker isolado na VPS Master que recebe webhooks externos (Tally / Cal.com / Asaas), valida autenticidade por fonte e ENFILEIRA jobs JSON num diretório (volume compartilhado com o consumer).

## Como funciona

- `GET /health` → `{status: ok}`.
- `POST /{tally|calcom|asaas}` → roteia pelo handler.
- Validação:
	- Tally + Asaas: header `X-Webhook-Secret` == `WEBHOOK_SECRET`.
	- Cal.com: `HMAC-SHA256(corpo, CALCOM_WEBHOOK_SECRET)` == `X-Cal-Signature-256`.
- Handler parseia payload e chama `integration._enfileirar(tipo, slug, **ctx)` → grava JSON em `ONBOARDING_QUEUE_DIR`.
- `dispatch.send_whatsapp` envia alerta leve via Evo (não-trava se falhar).
- `dispatch.create_linear_issue` cria issue via GraphQL (com retry).

## Handlers

| Endpoint | Job enfileirado | Notas |
|---|---|---|
| `/tally` | `consolidador` (slug, email, telefone, respostas) | Parseia `fields[]`, extrai nome/email/telefone, deriva slug |
| `/calcom` | `meeting` (trigger, slug, attendee*, inicio, uid, meeting_url) | BOOKING_CREATED/RESCHEDULED/CANCELLED |
| `/asaas` | `opp_move` (asaas_customer_id, payment_id, pipeline, stage_to) | só PAYMENT_RECEIVED/CONFIRMED + 1ª parcela (T-0); dedup `.seen` |

## Gotchas

- **F1 — Docker layer cache:** receiver buildava sem migração Stevo→Evo. `docker build --no-cache` virou padrão.
- **F3 — Telefone Cal.com:** cascata `attendees[0].phoneNumber → .phone → bookingFieldsResponses.attendeePhoneNumber → responses.phone → responses.attendeePhoneNumber`.
- **F4 — `cliente_registry`:** container não tem o pd-framework montado. Import best-effort silente, fallback slugify local. Gate de cliente é do consumer/skill `/ativar-cliente`, não do receiver.
- **F6 — Asaas opp_move:** receiver é stateless, não chama `cadencia-cli` direto. Enfileira `opp_move` pro consumer (mesmo padrão de `meeting`).

## Don'ts

- Não chamar `cadencia-cli` direto.
- Não importar nada do pd-framework (path).
- Não retornar 5xx em payload novo desconhecido — só loga + retorna 200.
- Não logar valor de secret.

## Relacionadas

- [[03-Consumer]] (consome a fila do receiver)
- [[01-Infra-Deploy]] (Docker, Traefik, env)
- [[07-Evo-Client]] (dispatch WhatsApp)
