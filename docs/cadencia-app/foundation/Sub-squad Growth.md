---
date: 2026-05-25
tags: [documentacao, cadencia, sub-squad, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
sub_squad: growth
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
> 📍 Origem: `times/produto/cadencia/growth/CLAUDE.md` no `pd-framework`. Última sync: 2026-05-25.

# Sub-squad growth — Cadência

> Sub-squad aninhado dentro do Squad pai Cadência. Criado em sessão guiada com Felipe (2026-05-25 — PDL-238).

---

## Escopo

Pipeline de geração e disparo de conteúdo via cron + scoring de leads via webhook. Opera na VPS Hostinger hoje, migrando para `/opt/cadencia-growth/` (PDL-213) e Coolify (PDL-215).

**Repo:** `Posicionamento-Digital/cadencia-growth`
**Deploy hoje:** VPS Hostinger `/cadencia/`
**Migração ativa:** `/opt/cadencia-growth/` + Coolify (cadeia PDL-213, PDL-215)

**Projeto Linear:** `3d140e11` — *Cadência Growth — Separação de Repo + Migração Railway → VPS*

---

## Workers / crons ativos

| Worker | Schedule | Função |
|---|---|---|
| Blog + Seinfeld | **11h BRT diário** (14 UTC) | Email storytelling diário + post blog tenant |
| LinkedIn | **11:30 BRT dias úteis** (14:30 UTC seg-sex) | Geração + pub LinkedIn (B2B window) |
| Newsletter | **12h BRT sexta** (15 UTC) | Consolidação posts da semana — Insight Artificial format |
| Webhook handler | `cadencia-webhook.service` systemd | Eventos GHL → lead scoring (+2/+5/+8/+20) |

Crontab fonte: `crons/crontab.txt` no repo.

---

## Pipeline (`pipeline/`)

| Arquivo | Função |
|---|---|
| `blog_generate.py` | Gera post blog tenant |
| `seinfeld_generate.py` | Gera email Seinfeld diário |
| `linkedin_generate.py` | Gera + publica LinkedIn |
| `newsletter_generate.py` | Consolidação semanal |
| `trigger_server.py` | Webhook handler systemd |
| `backfill_images.py` | Backfill imagens histórico |
| `brand_template.py` | Geração brand template por tenant |
| `prompts.py` | Centraliza prompts LLM |

---

## Scoring (`scoring/`)

- `cadencia-webhook.service` — systemd unit (sempre ON)
- `webhook_handler.py` — recebe eventos GHL e aplica scoring

**Faixas scoring:**
- +2: abriu email
- +5: clicou
- +8: abriu newsletter
- +20: WhatsApp engagement

Tags GHL automáticas: `interesse:automacao`, `interesse:gestao-ia`, etc — baseado em Seinfeld consumido.

---

## Migrations Supabase (`migrations/`)

- `001_seinfeld_scheduled_at.sql` — única até hoje
- Auditoria schema drift pendente (PDL-172 no Squad pai)

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Trigger | systemd unit + cron VPS |
| DB | Supabase (PostgreSQL + RLS) — mesmo Supabase do produto |
| LLM | OpenAI (via OpenRouter) — texto/copy |
| Imagens | Pexels (stock) + Gemini (capas) |
| CRM/email | GHL via API |
| Logs | `/cadencia/logs/growth_pipeline.log` |

---

## Workflows operacionais

- **Deploy hoje:** git pull no `/cadencia/` da VPS Hostinger + restart systemd se mudou webhook
- **Migração ativa:** PDL-213 mover pra `/opt/cadencia-growth/` + Coolify
- **Cron jobs:** crontab nativo VPS (não cron-job.org)
- **Validação pré-deploy:** compile check + dry-run com dados reais (skill `/validar-deploy-vps`)

---

## Pessoas

- **Felipe** — owner; opera scripts diretos
- **Time Dev cross-Time:** Vitor (arch migração), Amélia (dev)
- **Diego Infra (`times/infra/`)** — apoio na migração Coolify

---

## Bloqueios externos

| Bloqueio | Issue |
|---|---|
| Mover `/cadencia/` → `/opt/cadencia-growth/` | PDL-213 |
| Env vars Coolify 6 apps (In Progress) | PDL-215 |
| Validar race condition pós-migração + cancelar Railway | PDL-21 |
| Cron retention storage (depende política PDL-22) | PDL-23 |

---

## Histórico de incidents (do hub centralizado)

- **2026-05-15** — Ideias presas em status processing (spinner eterno frontend) — race condition Railway pega `generation_queue` antes do VPS
- **2026-05-04** — `corpo_claro` texto invisível (omissão recorrente NUCLEAR rule)
- **2026-04-25** — Race condition `generation_queue` Railway×VPS (blog nunca gerava)

---

## Foundation — consulta obrigatória

Antes de criar:
- Worker novo → `../foundation/tech-architecture.md` + `../foundation/multi-tenant-strategy.md`
- Política retention / cleanup → `../foundation/multi-tenant-strategy.md` § Storage
- Schedule novo / cron → considerar fuso (BRT vs UTC), conflitos com workers existentes
- Prompt LLM → `../SOUL.md` § Voz/tom + `../foundation/target-customers.md`

---

## Convenções

- **Branches:** `feat/pdl-XX-<desc>` no repo `cadencia-growth`
- **Commits:** convencional (`feat(growth):`, `fix(growth):`)
- **Logs:** sempre em `/cadencia/logs/` (path legado) — migrar pra `/opt/cadencia-growth/logs/`
- **Cron edits:** sempre via `crontab -e` + commit do `crons/crontab.txt` espelhando o estado

---

## Refs

- `memory/STATE.md` — estado atual
- `memory/decisions.md` — decisões específicas
- `../CLAUDE.md` — manual Squad pai
- `../foundation/tech-architecture.md` § Growth pipeline
- Repo: `Posicionamento-Digital/cadencia-growth`
- Projeto Linear: `3d140e11` (Cadência Growth — Separação Repo + Migração VPS)
