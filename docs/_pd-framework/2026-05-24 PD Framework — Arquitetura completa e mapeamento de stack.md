---
date: 2026-05-24
tags: [ia, framework, agentes, arquitetura, pd, vps]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Arquitetura Completa e Mapeamento de Stack

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


> Sessão de design 24/05/2026. Complementa as notas de 23/05.
> Projeto Linear: PD Framework — Squads, Stamper, Memória Operacional

---

## O problema que estamos resolvendo

Stack atual cresceu de forma orgânica e tem 5 problemas:
1. Skills soltas em `~/.claude/skills/` sem hierarquia ou dono claro
2. Memória via session logs — append-only, não consultável por agente
3. Contexto de cada área disperso em vaults, Linear, logs, pastas
4. Abrir Rotina/ carrega tudo junto — flood de contexto garantido
5. Agente que vai trabalhar num bug do Cadência precisa vasculhar monorepo gigante — contexto explode antes de começar

---

## Inspirações e o que foi aproveitado

### AIOX Core
- **STATE.md como documento vivo** (não append-only)
- **Bracketed loading**: L1 (status, ~50 tokens) → L2 (em progresso) → L3 (histórico completo)
- **Workers com autoridade exclusiva** por squad
- **Session digests** → virou `/fechar-squad` skill

### Hermes Agent (nousresearch)
- **Dual-store**: STATE.md (injeção de contexto, volátil) + decisions.md (histórico durável, nunca truncado)
- **recallMode hybrid**: STATE.md carregado automaticamente ao abrir squad + skill `/status <area>` para busca explícita

---

## As três camadas de cada squad

```
SOUL.md    → identidade imutável do produto (só produtos — Cadência sim, Squad GHL não)
CLAUDE.md  → manual operacional do agente (todos, obrigatório)
STATE.md   → situação atual do domínio (todos, obrigatório — muda todo dia)
```

### Formato padrão do STATE.md (bracketed)

```markdown
# STATE — [Área] (atualizado YYYY-MM-DD HH:MM)

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## [L1] Status agora
3 linhas max — situação atual. Stamper lê sempre.

## [L2] Em progresso
O que está sendo trabalhado. Stamper lê quando o assunto pede.

## [L3] Decisões e histórico
Decisões recentes. Migra para decisions.md quando crescer.
```

---

## Estrutura do monorepo

```
pd-framework/
├── CLAUDE.md                    ← roteador mínimo (só aponta para squads)
├── CONTEXT.md                   ← documentação da arquitetura
│
├── stamper/                     ← único ponto de entrada do Felipe
│   ├── CLAUDE.md                ← Doug Stamper persona completa
│   ├── memory/                  ← memória pessoal do Felipe (auto-memory)
│   ├── skills/                  ← abrir-dia, fechar-dia, status, log-sessao...
│   └── context/
│       ├── perfil-felipe.md
│       └── stack-ativa.md
│
├── squads/
│   ├── _core/                   ← runtime compartilhado
│   │   ├── memory-schema.md     ← schema padrão do STATE.md
│   │   ├── state-updater.py     ← worker que atualiza STATE.md
│   │   └── harness.sh           ← executor de workers na VPS
│   │
│   ├── comercial/
│   │   ├── CLAUDE.md
│   │   ├── memory/
│   │   │   ├── STATE.md
│   │   │   └── decisions.md
│   │   ├── skills/
│   │   └── workers/
│   │       ├── sync-ghl.py
│   │       ├── score-leads.py
│   │       └── crons/schedule.yaml
│   │
│   ├── marketing/
│   │   ├── CLAUDE.md
│   │   ├── memory/
│   │   │   ├── STATE.md
│   │   │   └── decisions.md
│   │   └── workers/
│   │       ├── disparo-seinfeld.py
│   │       ├── disparo-blog.py
│   │       ├── disparo-newsletter.py
│   │       ├── meta-ads-orchestrator.py
│   │       └── crons/schedule.yaml
│   │
│   ├── produto/
│   │   ├── CLAUDE.md
│   │   ├── memory/
│   │   │   ├── STATE.md
│   │   │   └── decisions.md
│   │   └── cadencia/            ← sub-produto com identidade própria
│   │       ├── CLAUDE.md
│   │       ├── SOUL.md
│   │       ├── memory/
│   │       │   ├── STATE.md
│   │       │   └── decisions.md
│   │       ├── skills/
│   │       │   ├── criar-tenant-agencia
│   │       │   └── tally-form-cadencia
│   │       └── workers/
│   │           ├── growth_pipeline.py
│   │           ├── retry_provisioning.py
│   │           ├── mission_control.py
│   │           └── crons/schedule.yaml
│   │
│   ├── infra/
│   │   ├── CLAUDE.md
│   │   ├── memory/
│   │   │   ├── STATE.md
│   │   │   └── decisions.md
│   │   ├── skills/
│   │   │   ├── vps-dev
│   │   │   ├── vps-master
│   │   │   ├── espelhar-repo-vps
│   │   │   └── validar-deploy-vps
│   │   └── workers/
│   │       ├── monitor-vps.sh
│   │       ├── webhook-receptor.py   ← Observabilidade
│   │       ├── auto-fix-agent.py     ← Observabilidade
│   │       └── crons/schedule.yaml
│   │
│   ├── cs/
│   │   ├── CLAUDE.md
│   │   ├── memory/
│   │   │   ├── STATE.md
│   │   │   └── decisions.md
│   │   ├── skills/
│   │   │   ├── ata-reuniao
│   │   │   ├── transcrever-reuniao
│   │   │   ├── busca-reunioes
│   │   │   ├── daily-luiz
│   │   │   └── ver-dia-luiz
│   │   └── workers/
│   │       └── lara/
│   │
│   └── operacional/
│       ├── CLAUDE.md
│       └── memory/
│           ├── STATE.md
│           └── decisions.md
│
└── _shared/
    ├── linear_client.py
    ├── stevo_client.py
    ├── obsidian_client.py
    ├── op_client.py
    ├── supabase_client.py
    ├── vercel_client.py
    ├── ghl_client.py
    └── email_client.py
```

---

## Dois modos de operação

### Autônomo (VPS Master — 72.60.4.71)
```
Cron → harness.sh → Worker executa → state-updater.py atualiza STATE.md → log
```

### Interativo (máquina local)
```
Felipe abre squads/<area>/ → Claude carrega CLAUDE.md + STATE.md → trabalha → /fechar-squad atualiza STATE.md
```

O STATE.md é o elo entre os dois modos.

---

## Obsidian na VPS — solução adotada

Obsidian requer GUI — não roda em servidor headless. Solução em duas partes:

**Workers na VPS não escrevem no Obsidian diretamente.** Escrevem em dois lugares:
1. `STATE.md` do squad — memória operacional da máquina
2. `queue/` folder no pd-framework — notas pendentes de criação no Obsidian

**Ponte local (Windows Task Scheduler):** cron local lê `pd-framework/queue/`, cria as notas via Obsidian CLI e limpa a fila. Obsidian Sync distribui para todos os dispositivos.

```
VPS worker → queue/nota.md (no repo pd-framework)
    ↓ git push
Local cron (Task Scheduler) → git pull → obsidian CLI cria nota → limpa queue/
    ↓
Obsidian Sync → mobile, outros dispositivos
```

**Casos de uso autônomos que precisam de Obsidian:**
- Relatório semanal gerado por worker
- ATA de reunião processada automaticamente
- Alertas e incidentes documentados

**Casos que não precisam:** STATE.md updates, logs de execução, métricas operacionais — esses ficam no pd-framework.

---

## Mecanismo de atualização do STATE.md

1. **Interativo** → skill `/fechar-squad <area>` ao encerrar sessão
2. **Autônomo** → worker cron via state-updater.py na VPS

---

## Vercel — projetos ativos

| Projeto | URL | Squad |
|---|---|---|
| `cadencia-app` | cadencia.ia.br | Produto/Cadência |
| `pd-portal` | pd-portal-kappa.vercel.app | Produto/PD Portal |
| `src` | insightartificial.ia.br | Marketing |
| `quartz-pd` | quartz-pd.vercel.app | Infra |
| `cadencia-blog-template` | cadencia-blog-template.vercel.app | Produto/Cadência |
| `blog-cadencia` | blog-cadencia.vercel.app | Marketing |
| `blog-petrafix-engenharia` | — | CS |
| `blog-certadoc` | — | CS |
| `blog-oral-prime-gold` | — | CS |
| `blog-letelog-operador-logistico` | — | CS |
| `blog-jhonatan` | — | CS |
| `blog-rovan-castro` | — | CS |
| `blog-felipe-luis-salgueiro` | — | Stamper/pessoal |

## Railway — ⚠️ em migração para VPS Master

Projeto único `cadencia` (production) — workers rodando como serviços. Ambiente "Pipelines PD" encerrado. Workers migram para `squads/produto/cadencia/workers/` na VPS Master.

---

## Mapeamento de integrações por squad

| Squad | Integrações | Modo |
|---|---|---|
| Stamper | Linear, Google Calendar, Obsidian, Stevo WhatsApp, Fireflies | skill |
| Comercial | GHL, Email outreach, scoring webhook | worker + skill |
| Marketing | Email, Meta Ads, Instagram, LinkedIn, Vercel | worker |
| Produto/Cadência | Supabase, N8N, Vercel, GHL, Tally, Railway→VPS | worker + skill |
| CS | Ecuro, Obsidian (Time PD vault), Linear, Vercel (blogs) | worker + skill |
| Infra | Grafana, Netdata, Cloudflare, Coolify, SSH, Sentry | worker + skill |

---

## O que roda na VPS Master hoje → squad destino

| Worker/Serviço | Squad | Tipo |
|---|---|---|
| disparo-seinfeld, blog, newsletter, ideacao | Marketing | cron |
| meta-ads/orchestrator, insight-artificial | Marketing | cron |
| scoring/inatividade_job, clustering | Comercial | cron |
| scoring-webhook.service | Comercial | systemd |
| cadencia growth_pipeline, retry_provisioning | Produto/Cadência | cron |
| cadencia mission_control, trigger_server | Produto/Cadência | @reboot |
| cadencia-webhook.service | Produto/Cadência | systemd |
| lara daily_summary, ecuro_sync, funnel_report | CS | cron |
| monitor-vps.sh | Infra | cron */5min |
| alloy (Grafana), netdata | Infra | systemd |
| cloudflared | Infra | systemd |
| stamper-bot (Telegram) | Stamper | systemd → migrar |

---

## Projeto: Central de Observabilidade + Auto-correção com IA

Vive dentro do Squad Infra. Fluxo:
```
Erro (Sentry/Netdata/Grafana) → webhook-receptor.py → issue Linear (auto-fix)
→ auto-fix-agent.py (cron) → tenta corrigir → fecha issue ou escala
→ STATE.md infra atualizado
```
Restrição: NUNCA tocar em cadencia-n8n, workers, postgres/redis, cloudflared.

---

## Decisões da sessão

- OpenClaw depreciado — integração GHL reconstruída nativamente no Squad Comercial (fase 2)
- Hierarquia máxima 3 níveis: Stamper → Área → Squad
- "Repo por feature" = isolamento de CONTEXTO, não de git repo
- Stamper sem STATE.md próprio — lê STATE.mds dos squads sob demanda
- SOUL.md só para produtos com identidade (Cadência sim, squads operacionais não)
- decisions.md separado — STATE.md substituído, decisions.md só cresce
- Obsidian na VPS via queue/ folder + cron local (Task Scheduler)

---

## Fases de implementação

1. Estrutura base — monorepo, CLAUDE.md raiz, migrar Stamper, memory-schema.md
2. Squad Infra — CLAUDE.md, STATE.md, harness.sh na VPS
3. Squad Comercial — STATE.md pipeline, workers, primeiro cron autônomo
4. Squads restantes — Marketing, Produto/Cadência, CS, Operacional
5. _shared — consolidar scripts, testar handoff Stamper → squad

---

## Notas Relacionadas

[[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]]
