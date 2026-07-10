---
date: 2026-05-24
tags: [ia, framework, squads, arquitetura, decisoes]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Mapa Final e Decisões Consolidadas

> Sessão noite 24/05/2026. Consolida todas as decisões tomadas após varredura de Obsidian, VPS Master, VPS Dev, repos GitHub, pastas locais, processos comerciais/CS/marketing e OpenClaw legacy.
> Substitui referências anteriores como fonte de verdade do mapa.

---

## Realidade que motiva o framework

**Empresa hoje = Felipe (executa tudo) + Luiz (dev escopo limitado).** Matheus e Michael foram demitidos. Operação enxuta, automação máxima é critério de sobrevivência, não otimização.

O PD Framework existe pra:
1. Centralizar contexto operacional de todas as áreas em STATE.md vivos
2. Descarregar trabalho manual repetitivo em workers determinísticos
3. Permitir Felipe abrir uma área e ter contexto em segundos
4. Manter Luiz produtivo em escopo controlado (framework separado dele)

---

## Mapa final de squads (consolidado)

```
pd-framework/
├── CLAUDE.md (roteador mínimo)
├── CONTEXT.md, README.md, index.html
├── _core/
│   ├── HIERARCHY.md (3 níveis + exceção pra produtos complexos)
│   ├── PROJECT-TYPES.md (taxonomia de tipos de projeto)
│   ├── SECURITY.md (scripts determinísticos na Master, agente NUNCA)
│   ├── PATHS.md (paths externos: gravações, fireflies, vaults, materiais)
│   ├── PEOPLE.md (Felipe + Luiz, sem mais ninguém)
│   ├── LINEAR-CONVENTIONS.md (labels epic:*, repo:*, bloqueado, etc)
│   ├── REPO-MAP.md (label → path local + VPS)
│   ├── memory-schema.md (STATE.md bracketed L1/L2/L3)
│   ├── squad-template/
│   ├── render-html.py (gera index.html por squad)
│   ├── harness.sh (pull + execute + commit + push + alerta conflito)
│   └── state-updater.py
│
├── stamper/                                          ← orchestrator
│   ├── CLAUDE.md, README.md, index.html
│   ├── memory/ (auto-memory pessoal Felipe — migrada de ~/.claude/projects/)
│   ├── context/perfil-felipe.md, stack-ativa.md, regras-globais.md
│   └── skills/ (gestão pessoal: abrir-dia, fechar-dia, fechar-semana, log-sessao, ja-fiz, status, chefe-de-staff, mandar-whatsapp, ata-reuniao, transcrever-reuniao, busca-reunioes, daily-luiz, ver-dia-luiz, fechar-semana-luiz, issue-semana, gestao-atividades-projeto)
│
├── squads/
│   ├── comercial/                                    ← absorve OpenClaw legacy
│   │   ├── workers/jobs/ (run_check_leads, run_enrichment, run_cadencia, run_diagnostico)
│   │   ├── skills/ (cadencia-pipeline, touchpoint-assistant, gerador-rep-g, enriquecimento-cnpj, campanha-email, nova-implementacao, fechar-dia-comercial, fup-reagendamento, scoring-monitor)
│   │   └── context/ (icp.md, framework-call-vendas, scoring-system, links Obsidian Comercial/)
│   │
│   ├── marketing/                                    ← consolida Projeto Marketing PD
│   │   ├── workers/ (disparo-seinfeld, disparo-blog, disparo-newsletter, disparo-ideacao, disparo-clustering, meta-ads-orchestrator)
│   │   ├── skills/ (6 categorias: Pipelines, Geradores, Email Marketing, Performance, Infra, Manuais)
│   │   ├── context/ (identidade-visual, posicionamento, publico-alvo, construtor-narrativas, links Obsidian Marketing-PD/)
│   │   └── launches/cadencia-2026/ (lançamento ativo)
│   │
│   ├── cs/                                           ← área operacional, executada por Felipe
│   │   ├── workers/ (alerta-churn-silencioso, lembrete-fup-semanal, calcular-lhi, varredura-30d-sem-contato)
│   │   ├── skills/ (briefing-cliente, ativacao-contrato, kickoff, validacao-prompt, primeira-entrega, contato-semanal-pos-golive, reuniao-15-dias, reuniao-mensal, radar-upsell, plano-retencao, renovacao-anual)
│   │   └── context/ (links Obsidian CS/ + Processos/Manuais/Implementacao/)
│   │
│   ├── infra/                                        ← VPS, monitoring, runbooks
│   │   ├── workers/ (webhook-receptor já existe, runbook-executor a criar, monitor-vps, collect-custom-metrics)
│   │   ├── runbooks/<app>/<rule>.sh
│   │   ├── skills/ (vps-master, vps-dev, espelhar-repo-vps, validar-deploy-vps)
│   │   └── context/ (topologia, ALLOWLIST, links Obsidian Infra/)
│   │
│   ├── operacional/                                  ← RH, Cultura, Metas, Processos internos
│   │   ├── context/ (links Obsidian Time PD/RH, Cultura, Metas, Processos)
│   │   └── skills/ (poucos — agenda-call, fechar-mes)
│   │
│   ├── financeiro/                                   ← squad novo descoberto
│   │   ├── workers/ (futuros: emissao-nf, conciliacao-asaas)
│   │   ├── skills/ (gerar-rps, gerar-dre, controle-fiscal)
│   │   └── context/ (clientes, fiscal, links ClaudeCode/Finanças/)
│   │
│   └── produto/
│       ├── ferramentas-ia/                           ← produtos PD comercializáveis
│       │   ├── cadencia/                             ← SOUL — squad pai com 4 sub-squads
│       │   │   ├── SOUL.md, CLAUDE.md, context/
│       │   │   └── squads/
│       │   │       ├── frontend/                     ← src/app Next.js
│       │   │       ├── growth/                       ← cadencia-growth (pipeline conteúdo)
│       │   │       ├── workers/                      ← cadencia-workers (backend, futuro Coolify)
│       │   │       └── blog/                         ← cadencia-blog
│       │   └── pd-portal/                            ← SOUL (sem sub-squads)
│       │
│       ├── consultorias/                             ← clientes consultoria independentes
│       │   ├── nathalia/
│       │   └── padaria-milionaria/
│       │
│       ├── nskin/                                    ← SOUL — projeto independente
│       └── gci-go/                                   ← SOUL — cliente grande
│           └── (inclui Lara + Ecuro como componentes internos do GCI)
│
├── _shared/                                          ← clients reutilizáveis
│   ├── stevo_client.py
│   ├── linear_client.py
│   ├── obsidian_client.py
│   ├── op_client.py
│   ├── ghl_client.py                                 ← do OpenClaw legacy, subprocess+curl
│   ├── supabase_client.py
│   └── vercel_client.py
│
└── _archive/                                         ← histórico, não-ativo
    ├── azoto-academy/        (não é mais cliente)
    ├── berro/                (empreendimento antigo)
    ├── hco/                  (cliente antigo)
    ├── karina/               (por enquanto não)
    ├── openclaw/             (depreciado — Comercial v2 nativa)
    ├── pipedrive-antigo/     (CRM substituído por GHL)
    ├── recovery-hertzner/    (Michael takeover 05/26)
    ├── posicionamento-digital-inc/
    ├── legal-michael/
    └── franquia-gestor-ia/   (produto legado)
```

---

## Hierarquia — regra e exceção

**Padrão:** 3 níveis (Stamper → Área → Squad).

**Exceção** para produtos complexos com sub-áreas independentes: 4 níveis. Único caso confirmado: Cadência (squad pai com SOUL + 4 sub-squads). PD Portal/NSkin/GCI/Consultorias **não** se ramificam — são monolíticos.

Documentado em `_core/HIERARCHY.md`.

---

## SOUL.md — onde tem

| Squad | Tem SOUL? | Por quê |
|---|---|---|
| Cadência | ✅ | Produto com identidade própria, marca pública |
| PD Portal | ✅ | Produto interno mas com identidade |
| NSkin | ✅ | Projeto independente, identidade própria |
| GCI-GO | ✅ | Cliente grande, projeto com identidade própria |
| Consultorias (Nathalia, Padaria) | ❌ | Cliente sem identidade de produto |
| Cadência sub-squads (frontend, growth, workers, blog) | ❌ | São features do produto pai |
| Squads operacionais (Comercial, Marketing, CS, Infra, Operacional, Financeiro) | ❌ | Áreas de operação, não produtos |

---

## Decisões arquiteturais consolidadas

### Memória
- **Memória pessoal Felipe** centralizada em `stamper/memory/` (migrada de `~/.claude/projects/.../memory/`)
- **Memória de área** em `squads/<x>/memory/STATE.md` (vivo) + `decisions.md` (histórico)
- **Memória por cliente** em `squads/produto/<cliente>/memory/STATE.md` (independente por cliente)
- STATE.md formato bracketed L1/L2/L3 (do AIOX Core)
- `decisions.md` só cresce, STATE.md substituído

### Processos
**Processos não duplicam no framework.** Vivem no Obsidian Time PD (CS/, Comercial/, Marketing-PD/, Processos/) e framework referencia via `_core/PATHS.md`. Agentes seguem os processos lendo de lá.

### Sync git
- 3 clones: local Windows (Felipe interativo), VPS Dev user felipe (Felipe interativo SSH), VPS Master (workers determinísticos)
- VPS Master clona apenas pra rodar workers — Felipe nunca abre `claude` lá
- Hub GitHub central, repo privado no GitHub pessoal do Felipe
- `git pull --rebase` em todo entry point (cron + abrir-squad)
- Conflito STATE.md → VPS vence (`--theirs`) + alerta WhatsApp Stevo
- VPS escreve só em STATE.md + queue/obsidian/. NUNCA em CLAUDE.md/skills/workers
- Crons fora 09:00–17:30 BRT: madrugada 03:00–06:00, antes 08:00–08:55, depois 18:00–22:00
- Webhooks de cadência podem escrever STATE.md a qualquer hora (Squad Produto/Cadência é majoritariamente autônomo, conflito raro aceito)

### Segurança
- Workers na Master = **scripts determinísticos**. Nunca agente Claude com tool use
- Auto-fix v0 = `runbook-executor.py` determinístico
- Fluxo (c) aprovação WhatsApp pra casos novos — agente roda local/VPS Dev sob aprovação humana
- Allowlist de containers em `squads/infra/runbooks/ALLOWLIST.md` enforced no executor
- Credenciais sempre via 1Password, nunca em texto plano em docs/scripts commitados

### Obsidian na VPS
Workers não escrevem direto. Escrevem em `queue/obsidian/` no repo. Windows Task Scheduler local pull → Obsidian CLI cria nota → limpa queue → push.

### HTML por squad
- `index.html` gerado por squad — visualização humana rápida
- Gerado na **criação** do squad + regenerado em **mudança estrutural** (git pre-commit hook detecta)
- STATE.md/decisions.md mudando NÃO trigga regeneração (fluxo operacional, não estrutural)

---

## Squad Comercial absorve OpenClaw legacy

OpenClaw rodava como container Docker na VPS executando Claude Code autônomo. Não compatível com a regra "scripts determinísticos na Master". **Container será depreciado.**

O que migra pro `squads/comercial/`:
- **Workers (jobs Python):** `run_check_leads`, `run_enrichment`, `run_cadencia`, `run_diagnostico`
- **Skills (slash commands locais):** Cadência Pipeline, Touchpoint Assistant, Gerador REP-G, Enriquecimento CNPJ, Campanha Email, Nova Implementação (handoff CS), Fechar Dia, Registrar Script, FUP Reagendamento
- **Clients integrações** vão pra `_shared/`: ghl_client.py, supabase_client.py, etc

Bot Telegram (`@felipeluissalgueiro_bot`) — decisão pendente: manter como interface OU substituir por sessões interativas no Stamper.

---

## Stack operacional confirmada

| Ferramenta | Uso |
|---|---|
| Linear | Issues, sprints, projetos (Felipe + Luiz) |
| Obsidian (Time PD + Pessoal) | Fonte de verdade de processos, runbooks, atas, contexto |
| GitHub (org Posicionamento-Digital) | Código (cadencia-app, pd-portal, etc) |
| GitHub pessoal Felipe | pd-framework (privado) |
| GHL | CRM operacional, automações, comunicação com cliente |
| Asaas | Cobrança, faturamento |
| N8N | Automações internas (Cadência) |
| Tally | Formulários (briefing, pré-reunião CS) |
| Stevo | WhatsApp via número pessoal Felipe |
| Coolify | Deploy containers VPS Master |
| Grafana Cloud + Alloy + Loki | Observabilidade |
| 1Password | Credenciais — fonte única |

---

## Pessoas — `_core/PEOPLE.md`

```
Felipe Luis Salgueiro — CEO
  Executa: comercial, CS, produto, marketing, infra, financeiro, dev (decisões)
  Único decisor estratégico

Luiz Sidião — Dev
  Escopo limitado: cadencia-app, pd-portal
  Trabalha na VPS Dev (/home/luiz/) com framework próprio (a criar)
  Deploy via git push → Coolify
```

Sem Matheus, sem Michael, sem outros operadores. Toda automação deve assumir Felipe como único executor humano.

---

## Próximos passos (a virar issues no projeto Linear "PD Framework")

1. **Fase 0 — Bootstrap** (1-2h): criar repo + `_core/` + estrutura base + clone local + clone VPS Dev + clone VPS Master
2. **Fase 0.5 — Reorganizar pastas externas** (1h): criar `_Materiais-PD/` e `_Arquivo/` em OneDrive/Documentos, mover pastas, depois preencher PATHS.md
3. **Fase 1 — Stamper migrado** (3-4h): CLAUDE persona + memory pessoal + skills do dia-a-dia + context + adaptar auto-memory hook
4. **Fase 2 — Squads operacionais Felipe-dependentes** (4-5h): Infra (webhook já existe), Comercial (absorve OpenClaw), CS (críticos pra clientes ativos), Marketing, Financeiro, Operacional
5. **Fase 3 — Squad Produto** (5-6h): Cadência com sub-squads + PD Portal + NSkin + GCI-GO + Consultorias
6. **Fase 4 — Auto-fix observabilidade** (3-4h): runbook-executor + endpoint approve + integração webhook→STATE.md infra
7. **Fase 5 — Refatorar linear-criar-projeto v2** (3h): consultar `_core/PROJECT-TYPES.md` + roteamento automático por tipo
8. **Fase 6 — Framework do Luiz** (2-3h): repo pd-framework-luiz na org, escopo reduzido (só squads/produto/cadencia + pd-portal), clone na VPS Dev user luiz

**Bloqueios externos:**
- PDL-213 (mover `/cadencia/` → `/opt/cadencia-growth/`) — afeta paths Cadência Growth
- PDL-215 (env vars Coolify 6 apps) — afeta Fase 3 e Fase 6
- Migração `/root/` → `/opt/apps/` (projeto Migração VPS já concluído arquiteturalmente — Felipe vai migrar quando puder)

---

## Notas Relacionadas

- [[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapeamento real de squads e infraestrutura]]
- [[IA-Tecnologia/2026-05-24 PD Framework — SOUL.md vs CLAUDE.md vs STATE.md]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Estratégia de sync Git VPS e local]]
- [[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]]
- [[IA-Tecnologia/2026-05-23 AIOX Core — framework de orquestração de agentes]]
- [[Infra/Stack-Monitoramento-VPS-Master]]
- [[Comercial/Playbook/Playbook-Comercial-PD]]
- [[CS/Playbook-CS-Acompanhamento]]
- [[CS/Playbook-Checklist-Implementacoes]]
- [[Processos/Manuais/Implementacao/Playbook-Gestao-Interna-Clientes]]
- [[Processos/Gestao-Projetos-Dev]]
- [[Marketing-PD/Documentacoes/Posicionamento-Marca]]
- [[Marketing-PD/Documentacoes/Publico-Alvo]]
- [[Marketing-PD/Documentacoes/Construtor-de-Narrativas]]
- [[Marketing-PD/Documentacoes/Manual-Identidade-Visual-PD]]
- [[Comercial/SDR-Prospeccao/ICP-por-Categoria]]
- [[Comercial/Closers-Vendas/Framework-Call-Vendas]]
- [[Comercial/CRM-Gestao/Sistema-Scoring-Nutricao]]
