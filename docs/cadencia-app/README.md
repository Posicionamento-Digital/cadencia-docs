> **Cópia local — fonte de verdade no GitHub.**
> Origem: `Posicionamento-Digital/cadencia-app` → sincronizar via `/documentar`.

---

# Cadencia — Documentação Técnica

Cadencia é um SaaS multi-tenant de marketing automatizado com IA. Cada cliente (tenant) recebe um sistema autônomo que gera e publica conteúdo diário — blog, Instagram, newsletter, LinkedIn, email Seinfeld — calibrado com a identidade de marca do cliente.

## O que o sistema faz

```
Kickoff do cliente
  → Onboarding autônomo (dossier + editoriais + visual)
    → Pipeline diário de geração (blog, instagram, newsletter, LinkedIn, Seinfeld)
      → Publicação via GHL ou diretamente nos canais
        → Rastreamento de leads e scoring no CRM
```

Toda a geração acontece em workers Python rodando na VPS Master (cron 11h BRT). Carrosséis e reels rodam em Railway (GPU). O frontend Next.js na Vercel é a interface do cliente e do admin.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 14 (App Router) — Vercel |
| Banco | Supabase (PostgreSQL + RLS + Realtime) |
| Workers | Python — VPS Master (Coolify) |
| Carrossel/Reels | Python + Pillow/FFmpeg — Railway |
| CRM/automação | GoHighLevel (GHL) — motor invisível |
| Email | GHL Conversations API |
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
| `scoring.py` | Atualiza score de leads no GHL |

### Lib compartilhada (`/lib`)
- `supabase.ts` — cliente e helpers
- `ghl.ts` — wrapper da API GoHighLevel (location PIT token por tenant)
- `billing.ts` — consumo de créditos e planos Stripe
- `tenant.ts` — resolução de tenant por domínio

## Conceitos do domínio

**Tenant** — cliente do SaaS. Isolado por RLS Supabase (não DBs separados).

**Dossier** — perfil de marca gerado no onboarding. Alimenta toda a geração de conteúdo.

**Editorial** — 1 dos 3 pilares de conteúdo do tenant. Toda ideia pertence a 1 editorial.

**Location PIT token** — token de integração privada do GHL por tenant. Necessário para Seinfeld e scoring. Não confundir com `api_key`.

**Pipeline** — sequência diária de geração: `sync → blog → seinfeld → newsletter → linkedin → instagram`. Só roda para tenants com `onboarding_completed`.

## Decisões técnicas (ADRs)

| ADR | Decisão |
|---|---|
| [ADR-0001](adr/0001-stripe-em-vez-de-asaas.md) | Stripe em vez de Asaas para billing |
| [ADR-0002](adr/0002-chat-agent-design.md) | Design do chat agent de ideias |
| [ADR-0003](adr/0003-ghl-motor-invisivel.md) | GHL como motor invisível (não exposto ao cliente) |
| [ADR-0004](adr/0004-carrossel-railway-resto-vps.md) | Carrossel/reels em Railway, resto na VPS |
| [ADR-0005](adr/0005-location-pit-token-por-tenant.md) | Location PIT token por tenant |
| [ADR-0006](adr/0006-multi-tenant-rls-supabase.md) | Multi-tenant via RLS Supabase |

## Como navegar esta documentação

- **Arquitetura** — visão técnica completa, diagrama de componentes, CHANGELOG
- **Frontend** — páginas, API routes, auth, integrações
- **Workers** — cada worker documentado individualmente
- **Growth** — pipeline de conteúdo por canal
- **Lib** — schema Supabase, billing, integrações GHL
- **ADRs** — decisões técnicas com contexto e alternativas avaliadas

## Links

- **Repo:** [Posicionamento-Digital/cadencia-app](https://github.com/Posicionamento-Digital/cadencia-app) (privado)
- **Linear:** [linear.app/cadencia](https://linear.app/cadencia) — time CAD
- **Deploy:** Vercel (frontend) + VPS Master 72.60.4.71 (workers)
- **Supabase:** [app.supabase.com](https://app.supabase.com) — projeto `cadencia`
- **Coolify:** VPS Master → porta 8000
