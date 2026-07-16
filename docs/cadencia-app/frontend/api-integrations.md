# api-integrations — webhooks, CAPI e API interna

## TL;DR

Rotas de integração do Next.js para pagamentos Stripe, Meta CAPI e chamadas
internas autenticadas dos workers. Eventos de email/scoring chegam diretamente
ao daemon Resend/Svix do `cadencia-growth`.

## Identidade

- **Tipo:** Next.js API Routes
- **Paths:** `src/app/api/webhooks/`, `src/app/api/capi/`, `src/app/api/v1/`
- **Deps:** Stripe, Meta e workers Coolify VPS Master

## Webhooks

| Rota | Evento | O que faz |
|---|---|---|
| `POST /api/webhooks/stripe` | pagamento confirmado/refund | Credita ou ajusta a carteira com idempotência |
| daemon `cadencia-growth:8767` | eventos Resend/Svix | Atualiza score, atribuição e supressão no CRM |

## Meta CAPI

- Hash SHA256 de email/telefone antes do envio.
- Compartilha `event_id` com o pixel cliente para deduplicação.
- Requer `META_PIXEL_ID` e `META_CAPI_TOKEN` server-side.

## API interna v1

Workers usam `/api/v1/*` com shared secret para buscar dados ou registrar estado.
O navegador nunca chama essas rotas diretamente.

## Don'ts

- Não aceitar webhook Stripe sem validar `stripe-signature`.
- Não enviar PII em claro para CAPI.
- Não expor `/api/v1/*` sem autenticação e rate limit.
- Não processar o mesmo `event_id` duas vezes.

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Stripe retorna 400 | assinatura/env divergente | conferir `STRIPE_WEBHOOK_SECRET` |
| CAPI duplicada | `event_id` diferente no client/server | compartilhar a mesma chave |
| `/api/v1/*` 401 | shared secret divergente | alinhar Vercel e worker |

## Referências

- [payment-billing](../app/billing/CLAUDE.md)
- [scoring-leads](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/scoring-leads.md)
- [tracking-analytics](../../../lib/analytics/CLAUDE.md)
