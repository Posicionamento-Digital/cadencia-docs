---

> **ARQUIVO HISTORICO / LEGADO.** Preservado como memoria tecnica; nao descreve o runtime atual e nao deve ser usado como runbook operacional.
feature: billing-stripe-ghl
status: ✅ Produção
implementado_em: 2026-05-11
componentes_afetados:
  - src/lib/stripe.ts (novo)
  - src/lib/ghl.ts (novo)
  - src/lib/plans.ts (refactor)
  - src/app/api/app/checkout/route.ts (reescrito)
  - src/app/api/webhooks/stripe/route.ts (novo)
  - supabase/migrations/20260511000000_stripe_integration.sql (novo)
commits:
  - 74634b8 feat(billing): substitui Asaas por Stripe (big bang)
  - 674f620 feat(ghl): espelhar Stripe invoices pagas no GHL
  - 1a1d565 fix(ghl): payload de createInvoice com campos obrigatórios
  - 24e2634 fix(stripe): charge.refunded extrai tenant_id de subscription/payment_intent
  - 866e27b fix(ghl): mirror funciona pra one-time payments (addons)
---

# Billing — Stripe + Espelhamento GHL

> ⚠️ **Doc pré-PDL-505 (11/06/2026).** Este doc foi escrito quando o Cadência tinha planos recorrentes via Stripe Subscription. **Isso não existe mais** — o modelo migrou pra créditos puros (só `mode: "payment"` one-time, `CREDIT_PACKS` em `plans.ts`; sem `mode: "subscription"`, sem "Essencial/Profissional/Business/Growth Pro"). Fonte única do modelo atual: `times/produto/cadencia/MODELO-CREDITOS.md` (pd-framework). As seções abaixo que mencionam "assinar plano"/`mode=subscription` descrevem o fluxo **antigo** — mantidas como referência histórica do fluxo de webhook/GHL (que em boa parte ainda se aplica), mas **não confiar na parte de planos**.

## 📍 Identidade

| | |
|---|---|
| **Tipo** | Feature transversal (lib + API routes + DB + webhook + integração externa) |
| **Stack** | Next.js 15 (App Router) · Stripe SDK Node v17 · Supabase Postgres · GoHighLevel REST API v2 |
| **Conta Stripe** | Axis (BRL · livemode) |
| **Webhook endpoint** | `we_1TW0vXQnLaAmF0Bc1BQgJipi` → `https://cadencia.app.br/api/webhooks/stripe` |
| **GHL subaccount** | Cadencia — antiga PD (`PrAh9rKjmpUkElCu5KBI`) |
| **Status** | ✅ Produção. E2E validado com pagamento real + refund (11/05/2026). |

## ✨ TL;DR

Cliente paga no Stripe → webhook do Cadencia recebe → libera créditos no Supabase + cria invoice paga no GHL automaticamente. Refund segue caminho equivalente (status → `refunded`, tag GHL `refund-stripe`). Stripe é fonte da verdade; GHL é espelho de visualização/CRM.

## 🎯 Pra que serve

- ~~Cobrar planos recorrentes do SaaS Cadencia~~ **REMOVIDO (PDL-505)** — Cadência é créditos puros, sem assinatura
- Cobrar pacotes de créditos one-time (+10/+30/+60 créditos, `CREDIT_PACKS` em `plans.ts`)
- Cobrar clientes B2B de consultoria (GCI GO, Nathalia, Rogéria, Alvina) com regras específicas (cancel_at, send_invoice por boleto, parcelamento)
- Visualizar pagamentos/refunds no GHL Cadencia (CRM) sem código no GHL — webhook custom faz o trabalho

## ⚙️ Como funciona — fluxo end-to-end

### Pagamento (compra de créditos — fluxo atual, pós-PDL-505)

```
[1] Cliente em /app/plans clica num pacote de créditos (+10/+30/+60)
    ↓
[2] POST /api/app/checkout
     • Lê pacote de CREDIT_PACKS (plans.ts)
     • findOrCreateCustomer(stripe) — cria/recupera Customer
     • createCheckoutSession(stripe)
       - mode=payment (sempre — sem subscription desde PDL-505)
       - line_items: price stripe_price_id
       - metadata: {tenant_id, plan_slug}
     • Salva stripe_customer_id em tenant_config.config
     • Retorna session.url
    ↓
[3] Cliente redirecionado pra hosted page Stripe
    Paga com cartão
    ↓
[4] Stripe webhook → POST /api/webhooks/stripe
     verifyWebhookSignature() — valida assinatura whsec_*
    ↓
[5] Idempotência: SELECT em stripe_webhook_log
     Se já processou: retorna {status:"already_processed"}
     Se não: INSERT (processed=false)
    ↓
[6] Switch event.type:
     case checkout.session.completed:
       - INSERT em tenant_plans (status=active, créditos liberados)
       - Bridge GHL via Workers (Coolify VPS Master /api/v1/ghl/payment) — tag+pipeline _(GHL legado)_
       - mirrorPaidInvoiceToGhl():
         · stripe.customers.retrieve() → pega email
         · findContactByEmail() → busca Contact GHL
         · createInvoice() no GHL (paid + metadata stripe_invoice_id)
         · recordInvoicePayment() — marca como recebida
         · addContactTag(["cliente-pagante", "plano:<slug>"])
     case invoice.paid (renovação subscription):
       - Idempotência via stripe_invoice_id (evita criar duplicata se checkout.session já criou)
       - INSERT novo tenant_plans com créditos resetados
       - mirrorPaidInvoiceToGhl() (renewal)
    ↓
[7] UPDATE stripe_webhook_log SET processed=true
    ↓
[8] Cliente volta pra /app/plans/callback?status=success
    Vê os créditos liberados no /app
```

### Refund

```
[1] Operador clica Refund no Stripe Dashboard
    ↓
[2] Stripe webhook → POST /api/webhooks/stripe (event=charge.refunded)
    ↓
[3] Switch case "charge.refunded":
     Resolve tenant_id por cascata:
       a) charge.metadata.tenant_id
       b) charge.invoice → invoice.subscription_details.metadata.tenant_id
       c) charge.payment_intent → pi.metadata.tenant_id
     UPDATE tenant_plans SET status='refunded' WHERE plano ativo mais recente
     GHL: addContactTag(["refund-stripe"]) no contact correspondente
    ↓
[4] Cliente perde acesso aos créditos (app respeita status≠active)
```

## 🧠 Decisões arquiteturais

Ver [ADR-0001 — Stripe em vez de Asaas](../../adr/0001-stripe-em-vez-de-asaas.md).

Decisões secundárias:

- **Stripe é fonte da verdade, GHL é espelho.** Subscriptions criadas via API Stripe direto (não via funnel GHL). GHL recebe espelho via webhook custom (a integração nativa Stripe↔GHL NÃO puxa subs criadas externamente — só processa as que nascem no GHL).
- **Big bang Asaas → Stripe.** Sem feature flag, sem convivência. Justificativa: nenhum cliente pagante no SaaS na data do refactor.
- **Cartão only no SaaS.** Sem Pix/boleto pra reduzir fricção da Tiazinha Véia.
- **`send_invoice` pros B2B (boleto)** — Stripe hospeda página de pagamento, cliente escolhe método.
- **Nathalia consultoria com `cancel_at=2026-12-21`** em vez de Stripe Subscription Schedule (mais simples).
- **Idempotência via `stripe_webhook_log`** com `event_id` unique constraint. Garante que retentativas do Stripe não duplicam efeitos.
- **Mirror GHL é fire-and-forget dentro do webhook.** Erros do GHL NÃO derrubam o processamento do Stripe — logam e seguem.

## 🚫 Don'ts

- **Não criar subscriptions Cadencia SaaS direto no GHL** (Invoice Schedule) — GHL perde flexibilidade de proration/addons que a Stripe API oferece.
- **Não passar Stripe key em código** — sempre via `process.env.STRIPE_SECRET_KEY` (lazy init em `src/lib/stripe.ts`).
- **Não confiar em `charge.metadata.tenant_id`** — Stripe NÃO herda metadata da subscription pro charge. Sempre resolver via subscription/payment_intent. Esse foi o bug do commit `24e2634`.
- **Não exigir `session.invoice` no mirror GHL** — addons one-time têm `session.invoice=null` (Stripe só cria invoice pra subscriptions). Usar `payment_intent` ou `session.id` como fallback. Bug do commit `866e27b`.
- **Não enviar `name` vazio pro endpoint `/invoices/` do GHL** — 422 silencioso. Campos obrigatórios: `name`, `businessDetails`, `currency` por item. Bug do commit `1a1d565`.
- **Não void invoice GHL via API com PIT** — não suportado. Operação destrutiva precisa ser feita manualmente no Dashboard GHL ou via OAuth com scope diferente.

## 🔥 Troubleshooting

### Pagamento OK no Stripe mas créditos não liberaram no Cadencia
1. Conferir `stripe_webhook_log` no Supabase — webhook chegou? Foi `processed=true`?
2. Se não chegou: ver Webhook Deliveries no Stripe Dashboard (`https://dashboard.stripe.com/webhooks/we_1TW0vXQnLaAmF0Bc1BQgJipi`). Stripe mostra status HTTP por entrega.
3. Se chegou mas falhou: ver Vercel logs → `vercel logs cadencia-app`. Filtra por `Stripe webhook error`.
4. Verificar idempotência — se mesmo `event_id` foi processado antes, retorna `already_processed`. Apagar a row pra forçar reprocessamento (raríssimo).

### Invoice GHL não foi criada após pagamento Stripe
1. Vercel logs → buscar `mirrorPaidInvoiceToGhl error`.
2. Conferir `GHL_API_KEY` no Vercel é o PIT da subaccount certa (`PrAh9rKjmpUkElCu5KBI`). Comum: ter trocado de agência GHL e env zumbi apontando pra antiga.
3. Conferir email do customer Stripe bate com email do Contact GHL — `findContactByEmail()` retorna null se não houver match.
4. Se erro for 422 da `/invoices/`: regredir pro fix do commit `1a1d565` (campos obrigatórios `name`, `businessDetails`, currency por item).

### Refund Stripe não muda status no Supabase
- Versões antigas (antes do commit `24e2634`) tinham bug — `charge.metadata.tenant_id` é sempre vazio. Atualizar.
- Se ainda falha mesmo com commit novo: customer Stripe não tem subscription/PI metadata corretos. Migrar customer manualmente via SQL.

### Sub Stripe em trial não tem invoice ainda
- Esperado. Subscriptions criadas com `trial_end` futuro só geram invoice no fim do trial. Webhook `invoice.paid` dispara nesse momento.

### Múltiplos clientes Stripe compartilham mesmo email
- Caso real: 21 clínicas Sorria Rio/Vamos Sorrir usam `alicia.ramos@gci.com.br`. GHL não permite Contacts duplicados por email — 1 Contact GHL representa N customers Stripe. Não é bug.

## 🪦 Já tentamos

- **Integração nativa Stripe ↔ GHL pra ver subs criadas via API** — não funciona. Ela só conhece transações que nascem dentro do GHL (Invoice/funnel/payment link do próprio GHL). Validado em 11/05/2026 com `GET /payments/integrations/provider/whitelabel` retornando `providers:[]` mesmo após OAuth conectado.
- **Custom Provider GHL pra usar Asaas como gateway externo do GHL** — não é o que queremos. É o caminho inverso (`GHL → Stripe API`). Cadencia SaaS quer `Stripe API → GHL espelho`.

## 📚 Referências

### Código
- [`src/lib/stripe.ts`](../../../src/lib/stripe.ts) — cliente Stripe + helpers (lazy init pra Next build)
- [`src/lib/ghl.ts`](../../../src/lib/ghl.ts) — helpers GHL (findContactByEmail, createInvoice, recordInvoicePayment, addContactTag)
- [`src/lib/plans.ts`](../../../src/lib/plans.ts) — catálogo de planos com `stripe_price_id`
- [`src/app/api/app/checkout/route.ts`](../../../src/app/api/app/checkout/route.ts) — endpoint que cria Checkout Session
- [`src/app/api/webhooks/stripe/route.ts`](../../../src/app/api/webhooks/stripe/route.ts) — webhook handler (6 events + mirror GHL)
- [`supabase/migrations/20260511000000_stripe_integration.sql`](../../../supabase/migrations/20260511000000_stripe_integration.sql) — migration (stripe_webhook_log + colunas)

### Externos
- Dashboard Stripe: https://dashboard.stripe.com (conta Axis)
- Dashboard GHL: https://app.gohighlevel.com (subaccount Cadencia)
- Webhook endpoint Stripe: https://dashboard.stripe.com/webhooks/we_1TW0vXQnLaAmF0Bc1BQgJipi
- Stripe SDK Node docs: https://github.com/stripe/stripe-node
- GHL Invoices API: https://highlevel.stoplight.io/docs/integrations (rotas `/invoices/`)

### Decisões
- [ADR-0001 — Stripe em vez de Asaas](../../adr/0001-stripe-em-vez-de-asaas.md)

### Logs de sessão
- `Hub Projetos/Rotina/sessions-log/2026-05-11/cadencia-migracao-asaas-stripe-ghl_2026-05-11_2229.md`

## 📜 Histórico

| Data | Mudança | Commit |
|---|---|---|
| 2026-05-11 | Feature criada (big bang Asaas→Stripe + mirror GHL) | `74634b8`, `674f620` |
| 2026-05-11 | Fix payload `/invoices/` GHL (campos obrigatórios) | `1a1d565` |
| 2026-05-11 | Fix `charge.refunded` extrai tenant_id de subscription/PI | `24e2634` |
| 2026-05-11 | Fix mirror suporta one-time (addons sem session.invoice) | `866e27b` |
| 2026-05-11 | E2E validado em produção (pagamento R$49,90 → INV-000003 GHL automático em 1s; refund automático) | — |
