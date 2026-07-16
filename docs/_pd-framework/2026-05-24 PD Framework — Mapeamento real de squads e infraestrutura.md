---
date: 2026-05-24
tags: [ia, framework, squads, arquitetura, infraestrutura]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Mapeamento Real de Squads e Infraestrutura

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.




> Levantamento feito em 24/05/2026. Varreu GitHub personal + corporate, VPS Master, VPS Dev, Hub Projetos local, Time PD vault, Linear, Vercel, Railway.
> Complementa: [[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]]

---

## Squads reais — o que existe de fato

### Stamper (orchestrator)

| Componente | Onde |
|---|---|
| Rotina + skills | Hub Projetos/Rotina/ |
| Memory pessoal | ~/.claude/projects/*/memory/ |
| Bot Telegram | /opt/stamper-telegram-bot (VPS Master) |
| Repos GitHub | rotina (personal), claude-dev-skills (personal + corporate) |

---

### Squad Infra

| Componente | Onde |
|---|---|
| VPS Master | 72.60.4.71 — user master |
| VPS Dev | 2.24.117.172 — user felipe, user luiz |
| grafana-webhook | /opt/grafana-webhook (VPS Master — já existe!) |
| scripts | /opt/scripts (VPS Master) |
| Coolify, Traefik, Grafana/Alloy, Netdata | VPS Master systemd |
| cloudflared | VPS Master systemd |
| Quartz (publicação notas) | GitHub quartz-pd + Vercel quartz-pd.vercel.app |
| Docs infra | Time PD/Infra/ (Cloudflare/, N8N/, Obsidian/, VPS-Hostinger/) |
| Linear | Migração VPS produção ✅, VPS Dev Luiz ✅, Observabilidade (backlog) |
| Skills | vps-dev, vps-master, espelhar-repo-vps, validar-deploy-vps, registrar-incidente |

**Workers a criar (Observabilidade):**
- `webhook-receptor.py` — recebe alertas Sentry/Netdata/Grafana, cria issues Linear
- `auto-fix-agent.py` — lê issues `auto-fix`, tenta remediar, registra em STATE.md

---

### Squad Produto / Cadência

| Componente | Onde |
|---|---|
| cadencia-app | GitHub (personal + corporate), /opt/cadencia-app VPS Master, /home/felipe/cadencia-app VPS Dev |
| cadencia-growth | GitHub corporate (repo separado — conteúdo não inspecionado) |
| cadencia-blog-template | GitHub personal + Vercel cadencia-blog-template.vercel.app |
| assessoria-imprensa-cadencia | GitHub personal + /opt/assessoria-imprensa-cadencia VPS Master |
| Workers cron | VPS Master /cadencia/: pipeline, scoring, mission_control, crons/ |
| Railway | cadencia (production) — migração para VPS Master pendente |
| Vercel | cadencia-app (cadencia.ia.br), cadencia-blog-template, blog-cadencia |
| Linear | Cadência Roadmap (in progress), Cadência Bugs (in progress), Cadência Growth separação Railway→VPS (backlog) |
| Skills | criar-tenant-agencia, tally-form-cadencia |
| **Luiz ativo** | /home/felipe/cadencia-app no VPS Dev |

---

### Squad Produto / PD Portal

| Componente | Onde |
|---|---|
| pd-portal | GitHub (personal + corporate), /home/felipe/pd-portal VPS Dev |
| Vercel | pd-portal-kappa.vercel.app |
| Docs | Time PD/Projetos/pd-portal/, Projetos/Portal PD/ |
| Linear | Portal Clientes PD ✅ |
| **Luiz ativo** | /home/felipe/pd-portal no VPS Dev |

---

### Squad Marketing

| Componente | Onde |
|---|---|
| insight-artificial | GitHub (personal + corporate), /opt/insight-artificial VPS Master |
| pd-marketing | GitHub personal |
| marketingpd-railway | GitHub personal (legado Railway) |
| Hub Projetos local | Hub Projetos/Insight Artificial/ (tem CLAUDE.md, src, scripts, supabase!) |
| Vercel | insightartificial.ia.br, blog-cadencia.vercel.app |
| Workers | disparo-seinfeld, blog, newsletter, ideacao, meta-ads/orchestrator, cron_publish |
| Linear | Pipeline Marketing PD refatoração (backlog) |
| **Atenção** | Insight Artificial tem Supabase próprio em Hub Projetos — não estava no mapa anterior |

---

### Squad Comercial

| Componente | Onde |
|---|---|
| Scoring leads | /cadencia/scoring/ VPS Master (scoring-webhook systemd) |
| Workers | scoring/inatividade_job, clustering |
| OpenClaw | /opt/openclaw VPS Master, GitHub openclaw-state + openclaw-sales-bot — **DEPRECIADO** |
| REP Framework | Hub Projetos/ClaudeCowork_Sales/ (Framework_REP.md, gerador-abordagem) |
| Docs | Time PD/Comercial/ |
| Linear | Comercial Felipe (backlog), Proposta WGL energia B2B (aguardando) |
| **Fase 2** | Integração GHL nativa reconstruída dentro do Squad (após PD Framework estruturado) |

---

### Squad CS

| Componente | Onde |
|---|---|
| Lara IA | GitHub corporate lara-ai + /opt/lara-ai VPS Master |
| ecuro-mcp | GitHub corporate |
| meeting-transcriber | GitHub personal + Hub Projetos/meeting-transcriber/ |
| GCI GO | Hub Projetos/Grupo GCI GO/ (PRD, arquitetura, epics, stories) + GitHub gci-go-whatsapp |
| H&Co | Hub Projetos/Projeto H&Co/ |
| NSkin | Hub Projetos/Projeto NSkin/ |
| Cowork CS | Hub Projetos/Cowork_CustomerSucess/ (playbooks, CRM-PD, templates) |
| Blogs clientes | Vercel: petrafix, certadoc, oral-prime-gold, letelog, jhonatan, rovan-castro |
| Linear | Dra. Nathalia (in progress), GCI GO Confirmação Agenda (in progress), GCI GO Lara (in progress) |
| Skills | ata-reuniao, transcrever-reuniao, busca-reunioes, daily-luiz, ver-dia-luiz, fechar-semana-luiz |
| Workers | lara/: daily_summary, ecuro_sync, funnel_report |
| Docs | Time PD/CS/, Projetos/GCI-GO/, Projetos/ecuro-mcp/, Projetos/Karina Vieira/ |

---

### Squad Operacional

| Componente | Onde |
|---|---|
| Processos internos | Time PD/Processos/, RH/, Financeiro/, Cultura/, Metas/ |
| Workers | Nenhum ainda |
| Repos | Nenhum ainda |

---

## Descobertas que impactam a arquitetura

1. **`cadencia-growth` é repo corporativo separado** — não é código dentro do cadencia-app. Precisa inspeção antes de mapear no squad definitivo.

2. **`grafana-webhook` já existe em /opt/** — embrião do Squad Infra está vivo na VPS sem estrutura formal.

3. **Insight Artificial tem `supabase/` próprio** em Hub Projetos local — Squad Marketing tem dependência Supabase não mapeada; vai para `_shared/` ou dentro do squad?

4. **Luiz ativo em dois repos** (cadencia-app + pd-portal) no VPS Dev — Squad Produto tem colaborador ativo, o handoff Stamper → Squad Produto precisa considerar isso.

5. **`pd-framework/CONTEXT.md` já existe** em Hub Projetos — criado na sessão de 23/05. É a base do monorepo.

---

## O que falta para implementar (Fase 1)

- [ ] Criar estrutura de pastas do monorepo em `Hub Projetos/pd-framework/` (já tem CONTEXT.md)
- [ ] CLAUDE.md raiz (roteador mínimo)
- [ ] `squads/` com subpastas para cada squad
- [ ] `stamper/` com CLAUDE.md, memory/, skills/, context/
- [ ] `squads/_core/memory-schema.md` — schema padrão do STATE.md
- [ ] Criar issues no Linear para cada fase de implementação

---

## Notas Relacionadas

[[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]] · [[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]] · [[IA-Tecnologia/2026-05-23 AIOX Core — framework de orquestração de agentes]] · [[IA-Tecnologia/2026-05-24 PD Framework — SOUL.md vs CLAUDE.md vs STATE.md]]
