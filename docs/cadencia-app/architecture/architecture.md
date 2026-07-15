> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/architecture.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/architecture.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# Arquitetura — Cadência

> Diagrama C4 (Context + Container) em mermaid. Renderiza no GitHub preview e na wiki HTML.

## Nível 1 — Contexto (quem usa, com o que conecta)

```mermaid
graph TB
    Usuario[Usuário tenant<br/>do SaaS]
    Felipe[Felipe / Equipe PD<br/>operação]
    GHL[(GoHighLevel<br/>CRM brancado)]
    Stripe[(Stripe<br/>pagamentos)]
    LLM[(OpenAI / Gemini<br/>geração de conteúdo)]
    Mixpanel[(Mixpanel / PostHog<br/>GA4 / Meta)]
    Apify[(Apify<br/>análise Instagram)]
    Cron[(cron-job.org)]

    subgraph Cadencia [Cadência SaaS]
        App[Plataforma Cadência<br/>web + workers + pipeline]
    end

    Usuario -->|usa via browser/PWA| App
    Felipe -->|opera via mission control + skills| App
    App -->|provisiona subcontas<br/>dispara emails| GHL
    App -->|cria checkout<br/>recebe webhooks| Stripe
    App -->|gera texto/imagem/cover| LLM
    App -->|tracking server-side| Mixpanel
    App -->|análise concorrência| Apify
    Cron -->|dispara geração<br/>carrossel/reels| App
    GHL -->|webhooks scoring| App
```

## Nível 2 — Containers

```mermaid
graph TB
    Usuario[Usuário]
    GHL[(GoHighLevel)]
    Stripe[(Stripe)]
    LLM[(OpenAI / Gemini)]
    Cron[(cron-job.org)]

    subgraph Vercel [Vercel — Next.js]
        Frontend[Frontend<br/>Next.js 15 + React 19<br/>app + admin + marketing + onboarding]
        ApiRoutes[API Routes<br/>auth + billing + trigger<br/>webhooks + capi + stevo]
    end

    subgraph Workers [Coolify VPS Master — Workers Python]
        Workers[cadencia-workers<br/>FastAPI + Playwright<br/>orchestrator 7-step<br/>carrossel + reels + chat + onboarding]
    end

    subgraph VPS [VPS Master 72.60.4.71]
        Trigger[trigger_server<br/>:39090]
        GrowthCron[growth_pipeline.py<br/>cron 11h BRT]
        Seinfeld[seinfeld + newsletter + linkedin + blog + instagram<br/>scripts pipeline]
        Scoring[scoring webhook<br/>:8766]
        Mission[mission_control<br/>:8768]
    end

    subgraph Supabase [Supabase Cloud]
        DB[(PostgreSQL + RLS<br/>tenants / posts /<br/>onboarding / plans /<br/>dossier / editorials)]
        Storage[(Storage<br/>images + assets)]
        Auth[(Auth<br/>magic link + senha)]
    end

    Usuario --> Frontend
    Frontend --> ApiRoutes
    ApiRoutes --> DB
    ApiRoutes --> Auth
    ApiRoutes -->|carrossel/reels| Workers
    ApiRoutes -->|blog/seinfeld/linkedin/instagram| Trigger
    Workers --> DB
    Workers --> LLM
    Workers --> GHL
    Trigger --> Seinfeld
    GrowthCron --> Seinfeld
    Seinfeld --> DB
    Seinfeld --> GHL
    Seinfeld --> LLM
    Scoring --> GHL
    Scoring --> DB
    Cron -->|POST /api/app/trigger-generation| ApiRoutes
    GHL -.->|webhook email_opened/clicked| Scoring
    ApiRoutes -->|checkout| Stripe
    Stripe -.->|webhook| ApiRoutes
    Mission --> DB
```

## Nível 3 — Componentes principais

Ver `CLAUDE.md` raiz para lista completa dos 28 componentes com paths.

Resumo por área:

| Área | Componentes | Onde roda |
|---|---|---|
| **Frontend** | frontend-app, frontend-admin, frontend-onboarding, frontend-marketing, api-routes, api-auth-provisioning, api-integrations | Vercel |
| **Workers** | pipeline-orchestrator, theme-engine, onboarding-workers, chat-ideias, ideas-generator, instagram-publisher, rag-memory | Railway (migrando Coolify) |
| **Growth (VPS)** | growth-pipeline-runner, seinfeld-email, newsletter, linkedin-generation, blog-instagram-gen, scoring-leads, provisioning-ghl | VPS Master |
| **Lib/Infra** | lib-integrations, tracking-analytics, payment-billing, supabase-schema, blog-tenant | mix |

## Decisões arquiteturais

- [ADR-0001](adr/0001-stripe-em-vez-de-asaas.md) — Stripe substituiu Asaas (11/05/2026)
- [ADR-0002](adr/0002-chat-agent-design.md) — Design do chat "Tenho uma ideia"
- [ADR-0003](adr/0003-ghl-motor-invisivel.md) — GHL como motor invisível, nunca exposto na UI
- [ADR-0004](adr/0004-carrossel-railway-resto-vps.md) — Carrossel/reels em workers dedicados (hoje Coolify VPS Master; ADR-0012), blog/seinfeld/linkedin VPS
- [ADR-0005](adr/0005-location-pit-token-por-tenant.md) — `location_pit_token` por tenant (não global)
- [ADR-0006](adr/0006-multi-tenant-rls-supabase.md) — Multi-tenant via RLS Supabase (não DBs separados)

## Fluxos críticos

### Onboarding novo tenant

1. Signup → `tenants` + `users` + `tenant_onboarding (fase 1)` + `tenant_plans (trial, 3 créditos)`
2. Fire-and-forget `POST /api/v1/ghl/signup` → cria contato + opportunity em "Cadencia App [Clientes]"
3. `provision_tenant.py` (VPS) cria subconta GHL via agency PIT + snapshot → salva `location_pit_token` em `tenant_config`
4. Worker `dossier.py` gera dossier de marca
5. Worker `editorials.py` gera 3 editoriais
6. Visual: 15 presets, identity lock para cover (Gemini 2.5 Flash)
7. Pipeline diário começa a rodar quando `onboarding_completed=true`

### Geração diária (cron 11h BRT)

```
growth_pipeline.py
  ├─ sync (tenants + contatos)
  ├─ blog
  ├─ seinfeld --generate (agenda próximo)
  ├─ seinfeld --dispatch (envia hoje)
  ├─ newsletter (só sexta)
  ├─ linkedin
  └─ instagram
```

### Trigger on-demand (usuário aprova ideia)

```
POST /api/app/trigger-generation (Vercel)
  ├─ filtra carrossel/reels → workers Coolify VPS Master
  └─ outros canais → POST VPS:39090/trigger
       └─ run_pipeline(): sync → blog → seinfeld --generate → linkedin → instagram
          (newsletter é silenciosamente pulada — G002)
```

### Scoring (webhook GHL)

```
GHL workflow "email_opened"/"link_clicked"
  └─ POST http://72.60.4.71:8766
       ├─ resolve tenant por location_id (varre tenant_config)
       ├─ atualiza contact.score_ia + temperatura (GHL custom field)
       ├─ aplica tag score:aquecendo/quente/hot
       ├─ move opportunity no pipeline do tenant
       └─ persiste em scoring_events
```
