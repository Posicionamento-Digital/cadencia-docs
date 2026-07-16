# Cadencia

SaaS multi-tenant de marketing automatizado com IA. Cada cliente recebe um sistema autônomo que gera e publica conteúdo diário — blog, Instagram, newsletter, LinkedIn, email Seinfeld — calibrado com a identidade de marca do cliente.

## O que o sistema faz

```
Kickoff do cliente
  → Onboarding autônomo (dossier + editoriais + visual)
    → Pipeline diário de geração (blog, instagram, newsletter, LinkedIn, Seinfeld)
      → Publicação pelas integrações próprias de cada canal
        → Rastreamento de leads e scoring no CRM
```

Toda a geração acontece em workers Python rodando na VPS Master (cron 11h BRT). Carrosséis e reels rodam nos workers Coolify VPS Master (Railway DESLIGADO — cutover concluído, DEV-638). O frontend Next.js na Vercel é a interface do cliente e do admin.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 14 (App Router) — Vercel |
| Banco | Supabase (PostgreSQL + RLS + Realtime) |
| Workers | Python — VPS Master (Coolify) |
| Carrossel/Reels | Python + Pillow/FFmpeg — Coolify VPS Master (Railway DESLIGADO) |
| CRM/automação | CRM Cadência (Supabase + automações tenant-scoped) |
| Email | Resend + webhooks Svix |
| IA | GPT-4o, Gemini 2.5 Flash, DALL-E 3 |
| Billing | Stripe + créditos internos |

## Componentes principais

### Frontend (`/app`)
- **`/app`** — App do cliente: dashboard, chat de ideias, aprovação de conteúdo
- **`/admin`** — Painel interno: gestão de tenants, billing, observabilidade
- **`/onboarding`** — Fluxo de ativação do novo cliente (3 fases)
- **`/marketing`** — Site público (landing pages)

### Workers Python (VPS Master)
| Worker | Função |
|---|---|
| `growth_pipeline.py` | Orquestrador diário — roda todos os canais em sequência |
| `blog_instagram_gen.py` | Gera post de blog + caption Instagram |
| `seinfeld_pipeline.py` | Gera e despacha email diário Seinfeld |
| `newsletter_generator.py` | Compila e envia newsletter |
| `linkedin_generator.py` | Gera post LinkedIn |
| `ideas_generator.py` | Gera ideias de conteúdo automaticamente |
| `dossier.py` | Gera dossier de marca no onboarding |
| `editorials.py` | Define os 3 pilares editoriais do tenant |
| `resend_webhook.py` | Atualiza score e temperatura no CRM Cadência |

### Lib compartilhada (`/lib`)
- `supabase.ts` — cliente e helpers
- `tenant.ts` — resolução de tenant e acesso ao CRM próprio
- `billing.ts` — consumo de créditos e planos Stripe
- `tenant.ts` — resolução de tenant por domínio

## Conceitos do domínio

**Tenant** — cliente do SaaS. Isolado por RLS Supabase (não DBs separados).

**Dossier** — perfil de marca gerado no onboarding. Alimenta toda a geração de conteúdo.

**Editorial** — 1 dos 3 pilares de conteúdo do tenant. Toda ideia pertence a 1 editorial.

**CRM Cadência** — contatos, empresas, oportunidades, pipelines, tags, scoring e cadências isolados por tenant no Supabase.

**Pipeline** — sequência diária de geração: `sync → blog → seinfeld → newsletter → linkedin → instagram`. Só roda para tenants com `onboarding_completed`.

## Documentação completa

**https://posicionamento-digital.github.io/cadencia-docs/**

Cobre arquitetura, frontend, workers, ADRs, schema Supabase, gotchas, incidentes e onboarding de devs.

## Links

- **Linear:** [linear.app/cadencia](https://linear.app/cadencia) — time CAD
- **Deploy:** Vercel (frontend) + VPS Master 72.60.4.71 (workers)
- **Supabase:** projeto `cadencia`
- **Coolify:** VPS Master → porta 8000
