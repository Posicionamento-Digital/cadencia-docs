> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/app/api/webhooks/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/app/api/webhooks/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# api-integrations — webhooks, CAPI Meta, Stevo e v1

## TL;DR

4 grupos de rotas de integração: webhooks externos (Stripe + GHL), Meta Conversions API, WhatsApp Stevo e API interna v1 (workers Coolify VPS Master chamam daqui).

## Identidade

- **Tipo:** Next.js API Routes
- **Paths:**
  - `src/app/api/webhooks/` — Stripe + GHL
  - `src/app/api/capi/` — Meta CAPI
  - `src/app/api/stevo/` — WhatsApp QR
  - `src/app/api/v1/` — API interna
- **Status:** ativo
- **Deps:** Stripe, GHL, Stevo, Workers Coolify VPS Master

## Webhooks

| Rota | Evento | O que faz |
|---|---|---|
| `POST /api/webhooks/stripe` | Pagamento confirmado | Ativa plano, credita créditos |
| `POST /api/webhooks/ghl` | Eventos GHL | Roteia para VPS scoring `:8766` |
| `POST /api/growth/webhooks` | GHL location events | Valida `location_id` → scoring VPS |

## Meta CAPI (POST /api/capi)

- Hash SHA256 de email + phone do usuário
- Envia eventos de conversão ao Meta pixel server-side (mais confiável que client-side)
- Requer `META_PIXEL_ID` e `META_CAPI_TOKEN` em env

## Stevo (WhatsApp)

- `POST /api/stevo/qr` — retorna QR code atual
- `GET /api/stevo/status` — verifica se WhatsApp conectado
- Usado pela página `/conectar-whatsapp` (pública)

## v1 (API interna — workers Coolify VPS Master)

| Rota | Chamado por |
|---|---|
| `POST /api/v1/ghl/signup` | Workers após provisioning de tenant |
| `POST /api/v1/newsletter/generate` | Workers ao gerar newsletter |
| `GET /api/v1/*` | Workers precisam de dados do Supabase |

## Don'ts

- Webhook Stripe deve validar assinatura (`stripe-signature` header) — nunca remover essa validação
- `POST /api/growth/webhooks` roteia para VPS em produção — tem IP hardcoded, verificar se mudou com migração

---

## Quando usar

- Stripe envia webhook após pagamento confirmado → ativa plano + créditos.
- GHL envia webhook após eventos custom (location_created, contact_created etc).
- Meta CAPI: enviar conversão server-side em cada checkout/signup.
- Stevo QR/status para `/conectar-whatsapp`.
- Workers Coolify VPS Master chamam `/api/v1/*` para operações internas (signup GHL, status pipeline).

## Quando NÃO usar

- ❌ Webhooks sem verificação de assinatura — Stripe + GHL exigem signature header.
- ❌ CAPI com email/phone em texto claro — sempre SHA256.
- ❌ `/api/v1/*` exposto sem shared-secret — qualquer um pode chamar.

## Por que funciona assim

- Webhooks Stripe/GHL chamam Vercel (HTTPS público, baixa latência).
- CAPI server-side aumenta confiabilidade do tracking vs apenas Meta Pixel client.
- v1 é "internal API" — só workers/scripts internos chamam, com secret compartilhado.

## 🚫 Don'ts

- **Não** processar webhook 2x — idempotência via `event_id` Stripe / GHL.
- **Não** expor `STRIPE_WEBHOOK_SECRET` ou `META_CAPI_TOKEN`.
- **Não** mandar CAPI com PII em claro.
- **Não** confiar em payload GHL sem validar `location_id` no `tenant_config`.

## 🪦 Já tentamos

- **2026-04-23 — GHL webhook customdata categoria vazio**: ver incident.
- **2026-04-22 — Scoring webhook sem path evento ignorado**: ver incident.
- **2026-05-08 — GHL emails disparados para pacientes OG migração invoices**: webhook trouxe lista errada. Ver `2026-05-08_ghl-emails-disparados-pacientes-og-migracao-invoices.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Stripe webhook 400 signature | `STRIPE_WEBHOOK_SECRET` errado/desatualizado | Atualizar via Stripe dashboard |
| Pagamento confirmado, plano não ativou | Webhook idempotência rejeitou duplicata legítima | Verificar `event_id` dedup |
| GHL webhook não chega | URL configurada errada no GHL | Reconciliar `webhook_url` no GHL |
| CAPI evento duplicado | Sem dedup com client pixel | Garantir `event_id` único compartilhado |
| `/api/v1/*` 401 | Secret mismatch | Conferir env Vercel e worker |

## 📚 Referências cruzadas

- [payment-billing](../app/billing/CLAUDE.md)
- [scoring-leads](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/scoring-leads.md) — Consumidor downstream GHL
- [tracking-analytics](../../../lib/analytics/CLAUDE.md) — CAPI
