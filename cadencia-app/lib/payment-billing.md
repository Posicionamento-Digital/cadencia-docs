> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/app/api/app/billing/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/app/api/app/billing/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

> ⚠️ **Vocabulário desatualizado (DEV-989, 2026-06-30):** este doc descreve o fluxo em termos de "planos" — modelo anterior ao PDL-505 (11/06/2026). **Cadência não tem planos**, é créditos puros. Fonte única de vocabulário/modelo: `times/produto/cadencia/MODELO-CREDITOS.md`. A tabela "Planos e créditos" abaixo é **referência histórica dos price tiers do Stripe** (pode não refletir os produtos Stripe atuais — conferir `plans.ts`) — ao falar do modelo de negócio, usar sempre "carteira de créditos"/"créditos comprados", nunca "plano X". Correção completa do fluxo técnico (se o código ainda usa nomenclatura de plano internamente) é escopo de uma sincronização real com o repo `cadencia-app`, fora deste sweep de framework.

---

# payment-billing — pagamento e créditos (Stripe)

## TL;DR

Integração Stripe para compra de créditos (carteira de créditos por tenant — sem planos/assinatura, ver `MODELO-CREDITOS.md`). Migrado de Asaas em 11/05/2026.

## Identidade

- **Tipo:** Next.js API routes + Stripe
- **Paths:**
  - `src/lib/stripe.ts`
  - `src/app/api/webhooks/stripe/route.ts`
  - `src/app/(app)/app/plans/` (frontend)
  - `src/app/api/app/admin/billing/credits/` (admin)
- **Status:** ativo (Asaas deprecated, código ainda em `src/lib/integrations/` — dívida técnica)
- **Deps:** Stripe, Supabase (`tenant_plans`)

## Fluxo de compra

1. Usuário acessa `/app/plans`
2. Clica em plano → `POST /api/app/checkout` → cria Stripe Checkout Session
3. Redirect para Stripe → pagamento confirmado
4. Stripe envia `checkout.session.completed` webhook → `POST /api/webhooks/stripe`
5. Webhook: verifica assinatura → ativa plano → credita créditos em `tenant_plans`
6. Redirect para `/app/plans/callback` (confirmação)

## Planos e créditos

| Plano | Créditos | Preço |
|---|---|---|
| trial | 3 | R$ 0 |
| essencial | 30 | — |
| starter | 80 | — |
| profissional | 80 | R$ 399,90 |
| growth_pro | 9999 | R$ 1.497 |

Múltiplos `tenant_plans` com `status=active` somam créditos disponíveis.

## Dívida técnica

Código Asaas ainda presente em `src/lib/integrations/asaas.ts` — não remove operações ativas mas polui a lib. PDL pendente para remoção.

## Don'ts

- Nunca confiar no valor retornado pelo Stripe sem verificar `stripe-signature` — man-in-the-middle risk
- Não creditar créditos antes de confirmar pagamento no webhook (não na redirect page)

---

## Quando usar

- Compra/upgrade de plano no `/app/plans`.
- Crédito manual via admin (`/app/admin/billing/credits`).
- Recebimento de pagamento (`/api/webhooks/stripe`).

## Quando NÃO usar

- ❌ Asaas em código novo — descontinuado em 11/05/2026. Ver [ADR-0001](../../../../../docs/adr/0001-stripe-em-vez-de-asaas.md).
- ❌ Creditar antes de webhook confirmado — usuário pode cancelar antes do webhook.
- ❌ Confiar em redirect page para confirmar — `/plans/callback` é UI; webhook é fonte da verdade.

## Por que funciona assim

- [ADR-0001](../../../../../docs/adr/0001-stripe-em-vez-de-asaas.md) — Stripe substituiu Asaas.
- Múltiplos `tenant_plans` ativos somam créditos — permite addon sem refazer plano principal.
- Webhook assinado é fonte da verdade — redirect page só UX.

## 🚫 Don'ts

- **Não** ativar plano em redirect page — usar webhook.
- **Não** confiar em payload sem `stripe-signature`.
- **Não** processar webhook 2x para mesmo `event_id`.
- **Não** dar crédito manual sem audit log (admin).

## 🪦 Já tentamos

- Migração Asaas → Stripe em 11/05/2026. Razão: cobertura internacional, UX checkout, suporte recorrência mais maduro.
- Código Asaas em `src/lib/integrations/asaas.ts` ainda no repo — dívida técnica para limpar.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Pagamento OK, plano não ativou | Webhook não chegou / signature errada | Replayar via Stripe dashboard |
| Crédito duplicado | Webhook idempotência rejeitou re-tentativa | Conferir `event_id` dedup |
| Plano errado ativado | Mapping `price_id` → plan errado | Auditar `plans.ts` |
| Trial não criou | `provision-tenant` falhou pré-Stripe | Ver `api-auth-provisioning` |

## 📚 Referências cruzadas

- [api-integrations](../../webhooks/CLAUDE.md) — Webhook Stripe
- [api-auth-provisioning](../../auth/CLAUDE.md) — Cria plano trial
- [supabase-schema](../../../../../supabase/CLAUDE.md) — `tenant_plans`
- ADR: [0001 Stripe](../../../../../docs/adr/0001-stripe-em-vez-de-asaas.md)
