> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/lib/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/lib/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# lib-integrations — integrações externas (src/lib)

## TL;DR

Wrappers TypeScript para todos os serviços externos usados pelo frontend/API routes: GHL, Stripe, Instagram, analytics (Mixpanel/PostHog/GA4/Meta Pixel).

## Identidade

- **Tipo:** TypeScript modules
- **Path:** `src/lib/`
- **Status:** ativo
- **Deps:** GHL API, Stripe, Instagram Graph API, Mixpanel, PostHog, Meta Pixel, GA4

## Arquivos

| Arquivo | Serviço | Função |
|---|---|---|
| `ghl.ts` | GoHighLevel | CRUD contatos, oportunidades, conversas |
| `ghl-oauth.ts` | GHL OAuth | Troca de tokens, refresh, save em `ghl_agency_oauth` |
| `stripe.ts` | Stripe | Checkout, webhooks, assinaturas |
| `instagram.ts` | Instagram Graph API | Análise de perfil via Apify |
| `mixpanel.ts` | Mixpanel | Tracking de eventos de produto |
| `posthog.ts` | PostHog | Feature flags client-side + session recording |
| `meta-pixel.ts` | Meta Pixel | Eventos client-side (complementa CAPI) |
| `analytics.ts` | GA4 + unified | Analytics unificado |
| `utm.ts` | UTM params | Captura e preserva UTM params |
| `plans.ts` | Planos | Definição de planos, preços, créditos |

## GHL — ATENÇÃO

- `ghl.ts` usa `GHL_API_KEY` global (location central PD) para operações de signup
- `ghl-oauth.ts` gerencia tokens da agência (company-level)
- Cloudflare bloqueia urllib — usar `subprocess + curl` com User-Agent navegador nos workers Python

## Don'ts

- Nunca importar `ghl.ts` em componentes cliente — só em API routes (chaves server-side)
- `GHL_API_KEY` é global (location central), não por tenant — nunca usar para operações de contato do tenant

---

## Quando usar

- Wrappers TS para qualquer serviço externo. Server-side (API routes) só.

## Quando NÃO usar

- ❌ `ghl.ts` em componentes cliente — `GHL_API_KEY` é server-side.
- ❌ Para operações de tenant — use `location_pit_token` específico do tenant (não `ghl.ts` global). Ver [ADR-0005](../../docs/adr/0005-location-pit-token-por-tenant.md).
- ❌ Asaas em código novo — descontinuado (dívida pendente removeria).

## Por que funciona assim

- 1 arquivo por serviço — facilita rotação de credencial, mock em teste, swap de provider.
- `ghl.ts` usa location central PD apenas para tracking lifecycle dos próprios clientes Cadência.
- PostHog para feature flags client-side (não-críticas); `tenant_config` para flags críticas server-side.

## 🚫 Don'ts

- **Não** importar `ghl.ts` em client component (`'use client'`).
- **Não** usar `GHL_API_KEY` global para conteúdo de tenant (G004).
- **Não** colocar token no localStorage — server-only.
- **Não** usar PostHog para flags de billing/auth — fonte da verdade é `tenant_config`.

## 🪦 Já tentamos

- Tentar usar urllib Python contra GHL → bloqueado por Cloudflare. Solução: `subprocess + curl` com UA navegador.
- Asaas como gateway → migrado para Stripe ([ADR-0001](../../docs/adr/0001-stripe-em-vez-de-asaas.md)).

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| 403 ao chamar GHL | Cloudflare bloqueou UA default | Usar curl + Mozilla/5.0 |
| Token GHL expirou | OAuth precisa refresh | `ghl-oauth.ts` refresh; ver `provisioning-ghl` |
| Bundle TS grande | Importar wrapper em client | Verificar `'use client'` em chamador |
| Feature flag não atualiza | PostHog cache | Invalidate flags + reload |

## 📚 Referências cruzadas

- [payment-billing](../app/api/app/billing/CLAUDE.md) — Stripe
- [api-integrations](../app/api/webhooks/CLAUDE.md) — CAPI + Stevo
- [tracking-analytics](analytics/CLAUDE.md) — Mixpanel/PostHog/Meta
- ADRs: [0001 Stripe](../../docs/adr/0001-stripe-em-vez-de-asaas.md), [0003 GHL invisível](../../docs/adr/0003-ghl-motor-invisivel.md), [0005 PIT token](../../docs/adr/0005-location-pit-token-por-tenant.md)
