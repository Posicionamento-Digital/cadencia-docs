# lib/ — Lib + infra

5 componentes que servem o sistema todo (lib TS, infra DB, analytics, billing, blog white-label).

## Componentes

| Componente | Doc | Função em 1 linha | Stack |
|---|---|---|---|
| **Lib Integrations** | [lib-integrations.md](lib-integrations.md) | Wrappers TypeScript para GHL, Stripe, Instagram, Apify (server-side) | TypeScript modules |
| **Tracking Analytics** | [tracking-analytics.md](tracking-analytics.md) | Stack de 5 ferramentas: Mixpanel + PostHog + GA4 + Meta Pixel + CAPI | Client + server-side |
| **Payment Billing** | [payment-billing.md](payment-billing.md) | Stripe checkout + webhook + créditos por tenant (substituiu Asaas 11/05/2026) | Stripe + Next.js API |
| **Supabase Schema** | [supabase-schema.md](supabase-schema.md) | 55 tabelas PostgreSQL com RLS — multi-tenant via Row Level Security | Supabase Cloud |
| **Blog Tenant** | [blog-tenant.md](blog-tenant.md) | Blog white-label por tenant — 1 instância Vercel separada por tenant | Next.js standalone |

## Quando entrar em cada

**Vai integrar com serviço externo?** → `lib-integrations.md` (escolher wrapper certo) + ADR-0005 se for GHL.

**Vai mexer em tracking/conversão?** → `tracking-analytics.md` (entender qual ferramenta para qual evento).

**Vai mexer em pagamento/crédito/plano?** → `payment-billing.md` + ADR-0001 (Stripe substituiu Asaas).

**Vai escrever SQL/migration/policy?** → `supabase-schema.md` + ADR-0006 (RLS multi-tenant).

**Vai mexer no blog do cliente?** → `blog-tenant.md`.

## Cuidados transversais (Don'ts)

- **`GHL_API_KEY` é server-side** — nunca expor em client.
- **Service_role bypassa RLS** — usar com cuidado, audit log obrigatório.
- **Stripe é fonte da verdade de pagamento** — não acreditar em redirect page; só webhook assinado.
- **PII no Meta CAPI** — sempre SHA256.
- **PostHog para flag crítica** — não usar; ir em `tenant_config`.
- **`auth.uid()` direto em policy RLS** degrada perf — usar `(SELECT auth.uid())` (PDL-159 a 166).

## Refs

- Voltar: [`../README.md`](../README.md)
- ADRs: [0001 Stripe](../adr/0001-stripe-em-vez-de-asaas.md), [0005 PIT token](../adr/0005-location-pit-token-por-tenant.md), [0006 RLS multi-tenant](../adr/0006-multi-tenant-rls-supabase.md)
- Consumidor: [`../frontend/`](../frontend/) (API routes)
