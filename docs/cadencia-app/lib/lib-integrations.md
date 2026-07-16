# lib-integrations — integrações externas (`src/lib`)

## TL;DR

Wrappers TypeScript usados pelo frontend e pelas API routes para Stripe,
Instagram, analytics e serviços internos. Contatos, oportunidades e pipelines
usam o CRM Cadência via Supabase; email usa Resend no growth pipeline.

## Arquivos principais

| Arquivo | Serviço | Função |
|---|---|---|
| `stripe.ts` | Stripe | Checkout, pagamentos e webhooks |
| `instagram.ts` | Instagram/Apify | Análise e integração de perfil |
| `mixpanel.ts` | Mixpanel | Eventos de produto |
| `posthog.ts` | PostHog | Flags não críticas e session recording |
| `meta-pixel.ts` | Meta | Eventos cliente complementares à CAPI |
| `analytics.ts` | GA4/unified | Analytics unificado |
| `utm.ts` | UTM | Captura e preservação de parâmetros |
| `plans.ts` | Créditos | Pacotes, preços e regras da carteira |

## Regras

- Um wrapper por serviço, sempre server-side quando houver credencial.
- Não colocar tokens em `localStorage` ou bundles cliente.
- Não usar PostHog como fonte de verdade para billing ou auth.
- Toda operação multi-tenant precisa resolver e filtrar `tenant_id`.
- Serviços externos devem ter timeout, retry limitado e erro observável.

## Referências

- [payment-billing](../app/api/app/billing/CLAUDE.md)
- [api-integrations](../app/api/webhooks/CLAUDE.md)
- [tracking-analytics](analytics/CLAUDE.md)
