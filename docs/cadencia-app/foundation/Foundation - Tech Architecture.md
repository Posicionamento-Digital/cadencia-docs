---
date: 2026-05-25
tags: [documentacao, cadencia, foundation, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]", "[[marketing]]"]
---
> 📍 Origem: `times/produto/cadencia/foundation/tech-architecture.md` no `pd-framework`. Última sync: 2026-05-25.

# Tech Architecture — Cadência

> Stack consolidada do produto. Referência pra qualquer decisão técnica. Última revisão: 2026-05-25.
>
> **Esta é uma visão alto-nível.** Detalhes operacionais profundos (schemas, endpoints, runbooks) vivem em `../context/` ou no repo `cadencia-app/docs/`.

---

## Arquitetura macro

```
[Usuário] → [Cadência App (Next.js 15 / Vercel)]
                    ↓ proxy rewrite /api/v1/*
             [FastAPI Workers (Python 3.12 / Railway → Coolify)]
                    ↓
             [Supabase Cloud (PostgreSQL + RLS + Storage + Auth)]
                    ↓
        ┌──────────┼──────────┐
        ↓          ↓          ↓
   [OpenAI]   [Gemini]   [Playwright]
   conteúdo   capas      HTML→PNG
                    ↓
             [GHL (brancado)]
             CRM + email + WhatsApp + Social Planner
                    ↓
             [Blog Vercel por tenant (cadencia-blog-template)]
                    ↓
        ┌──────────┴──────────┐
        ↓                     ↓
   [Growth Pipeline       [Webhook scoring
    VPS Hostinger]        systemd]
   (cadencia-growth)
```

---

## Repos GitHub

| Repo | Org | Conteúdo | Deploy |
|---|---|---|---|
| `cadencia-app` | felipeluissalgueiro | Frontend Next.js (`src/`) + Workers Python (`cadencia-workers/`) — monorepo | Vercel (`main`) + Coolify VPS Master (`master`) |
| `cadencia-growth` | Posicionamento-Digital | Pipeline Python — blog/seinfeld/linkedin/newsletter + scoring webhook | VPS Hostinger `/cadencia/` → `/opt/cadencia-growth/` (migração PDL-213) |
| `cadencia-blog-template` | felipeluissalgueiro | Template Next.js multi-tenant para blogs gerados | Vercel auto-deploy por tenant |

---

## Frontend (`cadencia-app/src/`)

**Stack:** Next.js 15.5 + React 19.1 + TypeScript + Tailwind + shadcn/ui + Serwist (PWA)

**Áreas (route groups):**
- `(app)/` — app principal usuário cliente final
- `(admin)/` — admin interno (Felipe/equipe)
- `(marketing)/` — landing pages + marketing público
- `(onboarding)/` — Tour RPG 12 steps + provisioning
- `staff/` — gestão de tenants (área PD interna)
- `conectar-whatsapp/` — fluxo OAuth WhatsApp

**API routes (`src/app/api/`):**
- `app/` — endpoints app
- `auth/` — Supabase Auth handlers
- `capi/` — Meta CAPI tracking
- `growth/` — endpoints growth pipeline
- `instagram/` — Instagram OAuth + publisher
- `onboarding/` — fluxo onboarding
- `stevo/` — integração WhatsApp Stevo (multi-tenant)
- `v1/` — endpoints versionados
- `webhooks/` — webhooks externos (Stripe, GHL, Asaas legacy)

**Lib (`src/lib/`):** analytics, animations, api, ghl, ghl-oauth, instagram, meta-pixel, mixpanel, plans, posthog, stripe, supabase, utm

**Deploy:** push `main` → Vercel build automático.

---

## Workers backend (`cadencia-app/cadencia-workers/`)

**Stack:** Python 3.12 + FastAPI + Playwright (HTML→PNG) + Dockerfile + docker-compose Coolify _(railway.toml/Procfile = legado)_

**Pipeline 7-step orchestrator** (`src/workers/orchestrator.py`):
1. **Research Agent** — pesquisa tema (Método X/Y)
2. **Model Selector** — classifica em 12 flags → seleciona modelo YAML (29 disponíveis)
3. **Headline Agent** — headline + subtitle + hook_type
4. **Carousel Agent** — slides JSON com componentes visuais
5. **Caption Agent** — legenda Instagram + hashtags
6. **Cover Generation** — Gemini 2.5 Flash Identity Lock ou thematic
7. **Slide Renderer** — Playwright HTML→PNG 1080×1440 → Supabase Storage

**Agents adicionais:**
- `caption_agent/`, `carousel_agent/`, `chat_agent/`, `headline_agent/`, `research_agent/`
- `dossier.py` — Big5 + DPR + Kane + Archetypes
- `editorials.py` — 3 categorias post
- `ideas.py` — geração de ideias
- `instagram_publisher.py` — pub IG via OAuth
- `logo_analysis_agent.py` — análise logo
- `theme_agent.py` — tema
- `visual_identity.py` — VI generation
- `rag.py` — RAG
- `agent_memory.py` — memória dos agents
- `token_refresh.py` — refresh tokens OAuth

**Templates:** 7 famílias HTML (action / editorial / engagement / narrative / proof / statement / structured) + 29 modelos YAML.

**Integrations:** `asaas/` (legacy), `ghl/`, `llm/`, `pexels.py`, `supabase.py`.

**Tests:** orchestrator, slide_renderer, model_selector, cover_generation, llm_client, carousel_agent, model_config, nuclear_coverage, health + `visual/`.

**Deploy hoje:** push `main:master` → Railway (Dockerfile + healthcheck `/health`). **Migração ativa → Coolify VPS Master** (PDL-18 a 23).

---

## Growth pipeline (`cadencia-growth/`)

**Stack:** Python + Supabase + systemd (webhook handler)

**Crons VPS Hostinger** (`crons/crontab.txt`):

| Worker | Schedule | Função |
|---|---|---|
| Blog + Seinfeld | 11h BRT diário (14 UTC) | Email storytelling + post blog |
| LinkedIn | 11:30 BRT dias úteis (14:30 UTC seg-sex) | Geração + pub LinkedIn |
| Newsletter | 12h BRT sexta (15 UTC) | Consolidação semanal |

**Pipeline (`pipeline/`):**
- `blog_generate.py`, `seinfeld_generate.py`, `linkedin_generate.py`, `newsletter_generate.py`
- `trigger_server.py` — webhook handler systemd
- `backfill_images.py`, `brand_template.py`, `prompts.py`

**Scoring (`scoring/`):**
- `cadencia-webhook.service` (systemd unit)
- `webhook_handler.py` — eventos GHL → lead scoring (+2/+5/+8/+20)

**Migrações Supabase (`migrations/`):**
- `001_seinfeld_scheduled_at.sql` (única hoje)

**Deploy hoje:** `/cadencia/` na VPS Hostinger (path legado).
**Migração ativa:** `/cadencia/` → `/opt/cadencia-growth/` + Coolify (PDL-213, PDL-215).

---

## Banco de dados — Supabase

- **PostgreSQL** + **Row Level Security** em todas as tabelas multi-tenant
- **Storage** segmentado por tenant (bucket `tenant-photos` privado, slides públicos)
- **Auth** magic link + senha
- **Source of truth** — não duplicar estado em outro lugar

**Schema drift:** auditado via PDL-172 (pendente). Migrations versionadas no repo `cadencia-growth/migrations/` e `cadencia-app/`.

---

## CRM brancado — GHL (GoHighLevel)

- **Motor invisível** — usuário NUNCA sabe que existe GHL por baixo
- Cada tenant tem **subconta GHL** (provisionada no onboarding — bug ativo PDL-202)
- Email, WhatsApp, Social Planner via GHL
- OAuth: migração para nova agência pendente PDL-25 (aguardando Felipe)

---

## Pagamento — Stripe

- **Migrado de Asaas em 11/05/2026** (ADR 0001)
- Asaas ainda no código `integrations/asaas/` — dívida técnica (rip pendente)
- Webhooks recebidos em `/api/webhooks/stripe`

---

## LLM stack (fixa — trocar exige ADR)

| Função | Provedor | Modelo | Acesso |
|---|---|---|---|
| Texto (conteúdo, copy, headline) | OpenAI | gpt-* | via OpenRouter (`OPENAI_BASE_URL`) |
| Imagem (capa Identity Lock) | Google | Gemini 2.5 Flash | API direta |
| Análise Instagram (post + perfil) | Apify | scrapers IG | API |
| Stock images fallback | Pexels | — | API |

**PR ativo #2:** suporte a OpenRouter via `OPENAI_BASE_URL/OPENAI_MODEL` (workers).

---

## Tracking & Analytics

| Sistema | Função |
|---|---|
| **Mixpanel** | Eventos UI (browser) |
| **PostHog** | Session replay + feature flags |
| **GA4** | Web analytics (source of truth funil) |
| **GTM** | Tag manager unificado |
| **Meta Pixel + CAPI** | Tracking Meta Ads (dual-side) |
| **UTM tracking** | Todos emails + ads (breakdown por canal) |
| **Sentry** | Errors frontend + backend |
| **Vercel Analytics** | Web vitals (PR #1 em review) |

---

## Cron jobs

- **Hoje:** cron-job.org → triggers workers Coolify VPS Master
- **Migração:** Coolify cron nativo OU cron VPS Master

---

## CDN & infraestrutura externa

- **Cloudflare** — CDN
- **Vercel Edge** — deploy frontend + blog templates
- **Railway** — workers Python (migrando Coolify)
- **VPS Hostinger** (Master `72.60.4.71`) — destino migração workers + growth pipeline

---

## Decisões arquiteturais (ADRs formais)

- `docs/adr/0001-stripe-em-vez-de-asaas.md` — Stripe sobre Asaas (11/05/2026)

Próximas ADRs candidatas (não criadas ainda):
- Multi-tenant strategy formal (hoje em foundation, mas merece ADR)
- Migração Railway → Coolify (decisão arquitetural pendente formalizar)
- OpenRouter vs OpenAI direto (PR #2)

---

## Refs

- `../SOUL.md` — princípios técnicos não-negociáveis
- `tech-principles.md` — 8 princípios detalhados
- `multi-tenant-strategy.md` — isolation profundo
- `CLAUDE.md` repo `cadencia-app` — regras operacionais técnicas
- `_bmad-output/planning-artifacts/architecture.md` — arquitetura detalhada BMAD
