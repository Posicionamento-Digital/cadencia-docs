---
date: 2026-05-25
tags: [documentacao, cadencia, framework, playbook, squad]
moc: "[[MOC-Projetos]]"
projeto: Cadência (PD Framework)
status: ativo
---

# Cadência — Squad pai no PD Framework

> Playbook do Squad **Cadência** (path `times/produto/cadencia/` no `pd-framework`). Gerado em 2026-05-25 pela skill `/documentar`.
> Cópia do conteúdo vivo do repo + Wiki HTML local em `C:/Users/felip/OneDrive/Documentos/ClaudeCode/Hub Projetos/pd-framework/times/produto/cadencia/docs/wiki/index.html`.

## O que é

**Cadência** é o produto SaaS multi-tenant **Máquina de Posicionamento** com IA da PD. Este playbook documenta a estrutura do Squad no PD Framework — não substitui os MDs no repo, complementa.

cadencia.app.br · multi-tenant · GHL brancado · Next.js + Supabase + Workers Python.

## Hierarquia

```
times/produto/cadencia/            ← Squad pai PRODUTO
├── SOUL.md                        ← identidade (Maga + Sábia)
├── CLAUDE.md                      ← manual operacional + persona Catarina
├── memory/                        ← STATE atual + decisions
├── foundation/                    ← 5 docs constitutivos
├── context/                       ← snapshot Roadmap + Bugs
├── skills/                        ← 5 skills locais (debate + review-deploy + capi-test + gerenciar-plano + analytics-report)
├── features/blog/                 ← white-label template (PDL-240 rebaixado)
├── frontend/                      ← sub-squad Next.js 15
├── growth/                        ← sub-squad pipeline VPS + crons
└── workers/                       ← sub-squad Python backend
```

## Persona

**Catarina** — PM/Owner Cadência. Distinta de Paloma (PO Dev transversal). Inspirações: Marty Cagan (Inspired) + Teresa Torres (Continuous Discovery). Invocável `/catarina` cross-Time.

Voz: declarativa, parcimoniosa, sem entusiasmo vazio (alinhado SOUL Maga/Sábia).

## Foundation — 5 docs

- [[Cadencia-Framework/Docs/Foundation - Product Vision]]
- [[Cadencia-Framework/Docs/Foundation - Target Customers]]
- [[Cadencia-Framework/Docs/Foundation - Tech Architecture]]
- [[Cadencia-Framework/Docs/Foundation - Multi-Tenant Strategy]]
- [[Cadencia-Framework/Docs/Foundation - Tech Principles]]

## Sub-squads

- [[Cadencia-Framework/Docs/Sub-squad Frontend]] — Next.js 15 + Vercel
- [[Cadencia-Framework/Docs/Sub-squad Growth]] — Pipeline VPS + crons + scoring
- [[Cadencia-Framework/Docs/Sub-squad Workers]] — Python FastAPI + orchestrator 7-step

## Feature

- [[Cadencia-Framework/Docs/Feature Blog]] — white-label template `cadencia-blog-template`

## Bloqueios críticos vivos

| Bloqueio | Issue Linear | Sub-squad |
|---|---|---|
| GHL OAuth nova agência | PDL-25 (aguardando Felipe) | Squad pai |
| Subconta GHL onboarding | PDL-202 (P1) | Squad pai |
| generation_queue schema | PDL-171 (P1) | workers |
| Migração Railway → Coolify | PDL-18 a 23 (cadeia) | workers |
| `/cadencia/` → `/opt/cadencia-growth/` | PDL-213 | growth |
| Env vars Coolify 6 apps | PDL-215 (In Progress) | growth |
| Acesso Luiz Railway+Vercel | PDL-18 (aguardando Felipe) | Squad pai |

## Projetos Linear

- [Roadmap](https://linear.app/posicionamento-digital/project/prod-cadencia-roadmap-6475d91c6139/overview) — 37 issues (7 Done, 30 Todo)
- [Bugs](https://linear.app/posicionamento-digital/project/maint-cadencia-bugs-e-suporte-e740f1bc9bfb/overview) — 24 issues (11 Done, 12 Backlog, 1 In Progress)
- Growth Migração — projeto vinculado ao sub-squad `growth/`

## Como abrir o Squad

```
/abrir-squad times/produto/cadencia
```

Carrega CLAUDE.md + STATE.md + agrega L1 dos 3 sub-squads via `state-aggregator.py`.

## Skills disponíveis

Locais (`times/produto/cadencia/skills/`):
- `/cadencia-debate` — roundtable Catarina + Vitor + Amélia (decisões produto/arquitetura)
- `/cadencia-review-deploy` — Amélia adversarial + commit + push (no repo cadencia-app)
- `/capi-test` — testa endpoint CAPI Meta
- `/gerenciar-plano` — gestão de planos/créditos via Supabase
- `/analytics-report` — GA4 + PostHog + Mixpanel → Obsidian (migrado de Notion 25/05)

Globais:
- `/tally-form-cadencia` — briefing de marca via Tally
- `/criar-tenant-agencia` — provisioning white-glove

## Repos

- [`cadencia-app`](https://github.com/felipeluissalgueiro/cadencia-app) — frontend (src) + workers (cadencia-workers)
- [`cadencia-growth`](https://github.com/Posicionamento-Digital/cadencia-growth) — pipeline VPS
- [`cadencia-blog-template`](https://github.com/felipeluissalgueiro/cadencia-blog-template) — template white-label

## Histórico

- **2026-05-25** — Bootstrap completo Squad pai + 3 sub-squads + feature blog. PDL-232/237/238/239/240 fechadas via Closes. Persona Catarina criada. SOUL populado. 5 foundation docs. 5 skills (1 nova + 4 migradas A1 do repo).

## Notas relacionadas

- [[MOC-Projetos]]
- [[Cadencia/_README]] (vault de produto se existir)
- [[Time PD]]

## Wiki HTML local

`C:/Users/felip/OneDrive/Documentos/ClaudeCode/Hub Projetos/pd-framework/times/produto/cadencia/docs/wiki/index.html`
