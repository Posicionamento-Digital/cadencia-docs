# frontend/ — Next.js 15 (Vercel)

7 áreas do frontend `cadencia-app/src/app/`. Stack: **Next.js 15 App Router + React 19 + Tailwind + shadcn/ui + Serwist (PWA)**.

Deploy: **Vercel** com auto-deploy na branch `master`.

## Componentes

| Área | Doc | Path | Função em 1 linha |
|---|---|---|---|
| **Frontend App** | [frontend-app.md](frontend-app.md) | `src/app/(app)/app/` | App autenticado — 14 rotas (dashboard, ideias, agenda, performance, growth wrappers GHL) |
| **Frontend Admin** | [frontend-admin.md](frontend-admin.md) | `src/app/(app)/app/admin/` | Painel super_admin — 14 sub-rotas (tenants, custos LLM, model routing, flags, impersonate) |
| **Frontend Onboarding** | [frontend-onboarding.md](frontend-onboarding.md) | `src/app/(onboarding)/` | Fluxo 3 fases — perfil → dossier/identidade/editoriais → finalização |
| **Frontend Marketing** | [frontend-marketing.md](frontend-marketing.md) | `src/app/(marketing)/` + `src/app/conectar-whatsapp/` | Páginas públicas (landing, pricing) + QR WhatsApp |
| **API Routes** | [api-routes.md](api-routes.md) | `src/app/api/` | Overview dos 9 grupos de rotas |
| **API Auth/Provisioning** | [api-auth-provisioning.md](api-auth-provisioning.md) | `src/app/api/auth/` + `growth/oauth/` | `provision-tenant` (signup) + OAuth GHL callback |
| **API Integrations** | [api-integrations.md](api-integrations.md) | `src/app/api/webhooks/` + `capi/` + `stevo/` + `v1/` | Webhooks Stripe/GHL + Meta CAPI + WhatsApp Stevo + API interna v1 |

## Grupos de routes (9)

| Grupo | Path | O que faz |
|---|---|---|
| `app/` | `/api/app/*` | Operações app autenticado (conteúdo, ideias, créditos, admin, trigger-generation) |
| `auth/` | `/api/auth/*` | Auth + provision-tenant |
| `capi/` | `/api/capi/*` | Meta Conversions API server-side |
| `growth/` | `/api/growth/*` | OAuth GHL callback + growth |
| `instagram/` | `/api/instagram/*` | Análise perfil via Apify |
| `onboarding/` | `/api/onboarding/*` | Fluxo onboarding (fases 1, 2, 3) |
| `stevo/` | `/api/stevo/*` | WhatsApp Stevo (QR + status) |
| `v1/` | `/api/v1/*` | API interna — workers Coolify VPS Master chamam aqui |
| `webhooks/` | `/api/webhooks/*` | Stripe + GHL externos |

## Fluxo trigger-generation (mais crítico)

```
cron-job.org → POST /api/app/trigger-generation (Vercel)
  ├─ canal carrossel/reels → workers Coolify VPS Master
  └─ outros canais        → VPS :39090/trigger
```

## Cuidados transversais (Don'ts)

- **GHL nunca aparece em copy/UI** (ADR-0003) — usar "Cadencia Growth", "meus contatos".
- **`GHL_API_KEY` é server-side** — nunca importar `lib/ghl.ts` em client component (`'use client'`).
- **Score cards de Contatos são hardcoded "—"** (G003) — comportamento esperado, não bug.
- **Timeout Vercel** — 10s hobby, 60s pro. Operações longas → worker async.
- **Env var com trailing newline** quebra silenciosamente (`trigger_server` secret mismatch — incident 2026-04-26).

## Refs

- Voltar: [`../README.md`](../README.md)
- ADRs: [0003 GHL invisível](../adr/0003-ghl-motor-invisivel.md), [0005 PIT token](../adr/0005-location-pit-token-por-tenant.md)
- Lib que consome: [`../lib/`](../lib/)
- Workers para os quais delega: [`../workers/`](../workers/)
- Growth para o qual delega: [`../growth/`](../growth/)
