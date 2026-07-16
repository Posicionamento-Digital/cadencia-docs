---
date: 2026-05-25
tags: [ia, framework, arquitetura, definitivo, mapa, decisoes]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Arquitetura DEFINITIVA consolidada

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


> **Fonte de verdade definitiva** após Fase 0 (bootstrap) + Fase 0.7 em andamento (inventário) + auditorias VPS Master e VPS Dev em 25/05/2026.
> Substitui notas anteriores como referência primária. Notas de 23-24/05 ficam como histórico de design.
> Repo: https://github.com/felipeluissalgueiro/pd-framework (privado, pessoal Felipe)
> Linear project: PD Framework — Squads, Stamper, Memória Operacional (`7c31c484-a9b7-49e7-abda-78cf6f5e1ef0`)

---

## 1. Por que esse framework existe

**Empresa hoje = Felipe (CEO executa tudo) + Luiz (dev escopo limitado).** Matheus e Michael demitidos. Operação enxuta. **Automação máxima é critério de sobrevivência, não otimização.**

Problemas resolvidos:
1. Skills soltas em `~/.claude/skills/` sem hierarquia ou isolamento de contexto
2. Memória via session logs — append-only, serve auditoria humana, não consulta de agente
3. Contexto disperso entre vaults Obsidian, Linear, logs, pastas
4. Flood de contexto ao abrir Rotina/ (carrega tudo junto)
5. Agente não sabe estado atual de outra área sem Felipe repassar manualmente

---

## 2. Estrutura final do monorepo

```
pd-framework/
├── CLAUDE.md                    ← roteador mínimo
├── CONTEXT.md                   ← arquitetura + mapa + fases
├── README.md, .gitignore, .gitattributes
│
├── _core/                       ← runtime compartilhado
│   ├── HIERARCHY.md             ← 3 níveis padrão, 4 exceção Cadência
│   ├── PROJECT-TYPES.md         ← 6 tipos + fluxograma decisão (refinado)
│   ├── SECURITY.md              ← VPS Master determinística, 1P fonte única
│   ├── PATHS.md                 ← paths externos (preencher após Fase 0.5)
│   ├── PEOPLE.md                ← Felipe + Luiz
│   ├── LINEAR-CONVENTIONS.md    ← labels, statuses, branches, IDs cacheados
│   ├── REPO-MAP.md              ← repo:* → GitHub + Local + VPS Master + VPS Dev
│   ├── CLIs.md                  ← inventário CLIs por ambiente + exemplos reais
│   ├── CREDENTIALS.md           ← ponteiro mapa 1P + SA headless setup
│   ├── MCP-AND-APIS.md          ← MCPs CLI vs claude.ai + APIs REST/GraphQL
│   ├── INVENTORY.md             ← (outro agente populando — Fase 0.7)
│   ├── memory-schema.md         ← STATE.md bracketed L1/L2/L3
│   ├── squad-template/          ← boilerplate de squad
│   ├── render-html.py           ← gera index.html por squad
│   ├── harness.sh               ← cron entry point VPS (pull, exec, push, conflito)
│   └── state-updater.py         ← utilitário workers updaters STATE.md
│
├── _shared/                     ← clients Python (com fallback SA 1P)
│   ├── stevo_client.py          ← WhatsApp (número Felipe)
│   ├── ghl_client.py            ← GHL (curl + UA navegador)
│   ├── linear_client.py         ← Linear GraphQL
│   ├── obsidian_client.py       ← Obsidian CLI (só Windows)
│   ├── op_client.py             ← 1Password CLI
│   ├── supabase_client.py       ← Management API + PostgREST
│   └── vercel_client.py         ← Vercel REST
│
├── stamper/                     ← orchestrator (Fase 1 popula)
│   ├── CLAUDE.md                ← Doug Stamper persona completa
│   ├── memory/                  ← memória pessoal Felipe (migra de ~/.claude/projects/)
│   ├── context/                 ← perfil-felipe, stack-ativa, regras-globais
│   └── skills/                  ← abrir-dia, fechar-dia, ata-reuniao, etc
│
├── squads/                      ← áreas (Fases 2-3 populam)
│   ├── infra/                   ← VPS, monitoring, runbooks, webhook v2
│   ├── comercial/               ← absorve OpenClaw legacy
│   ├── cs/                      ← área operacional Felipe + workers críticos
│   ├── marketing/               ← consolida Marketing PD
│   ├── operacional/             ← RH, Cultura, Metas
│   ├── financeiro/              ← NF, Asaas, DRE
│   └── produto/
│       ├── ferramentas-ia/
│       │   ├── cadencia/        ← SOUL + 4 sub-squads (única exceção 4 níveis)
│       │   │   └── squads/{frontend, growth, workers, blog}/
│       │   └── pd-portal/       ← SOUL (monolítico)
│       ├── consultorias/        ← nathalia/, padaria-milionaria/
│       ├── nskin/               ← SOUL
│       └── gci-go/              ← SOUL (Lara + Ecuro como componentes internos)
│
├── _archive/                    ← inativos
│   ├── azoto-academy/, berro/, hco/, karina/
│   ├── openclaw/                ← uso comercial PD depreciar (image base Lara MANTÉM)
│   ├── pipedrive-antigo/, recovery-hertzner/
│   ├── posicionamento-digital-inc/, legal-michael/
│   └── franquia-gestor-ia/
│
├── .githooks/
│   └── pre-commit               ← regenera index.html em mudanças estruturais
│
└── docs/
    ├── git-sync-strategy.md     ← estratégia 3 clones
    ├── snapshots/
    │   ├── vps-master-2026-05-25.md
    │   └── vps-dev-2026-05-25.md
    └── plans/
        └── fase-4-auto-fix-observabilidade.md
```

---

## 3. As 3 camadas de cada squad

| Arquivo | Papel | Muda quando |
|---|---|---|
| `SOUL.md` | Identidade imutável do produto (missão, voz, valores) | Só se produto mudar fundamentalmente |
| `CLAUDE.md` | Manual operacional do agente (persona, escopo, regras) | Raramente |
| `STATE.md` | Situação atual (em progresso, bloqueios, próximas ações) | Todo dia / toda execução de cron |
| `decisions.md` | Histórico de decisões (append-only) | Quando há decisão relevante |

**SOUL.md tem:** Cadência, PD Portal, NSkin, GCI-GO. Sub-squads e operacionais **não**.

**STATE.md formato bracketed L1/L2/L3 (do AIOX Core):**
- L1: status agora (3 linhas max) — Stamper sempre lê
- L2: em progresso — lê quando o assunto pede
- L3: decisões recentes — só sob pergunta explícita

Detalhes: `pd-framework/_core/memory-schema.md`.

---

## 4. Hierarquia — regra e exceção

**Padrão:** 3 níveis (Stamper → Área → Squad).
**Exceção:** 4 níveis só para Cadência (squad pai com SOUL + 4 sub-squads: frontend, growth, workers, blog).

PD Portal, NSkin, GCI-GO, Consultorias **não** se ramificam — são monolíticos.

---

## 5. Memória — três escopos

- **Pessoal Felipe** → `stamper/memory/` (migrada de `~/.claude/projects/.../memory/`, agora versionada)
- **Área operacional** → `squads/<area>/memory/STATE.md` (vivo) + `decisions.md` (histórico)
- **Cliente/produto independente** → `squads/produto/<x>/memory/STATE.md`

Sessions logs continuam em `Rotina/sessions-log/` — auditoria humana.

---

## 6. Dois modos de operação

### Autônomo (VPS Master 72.60.4.71)

```
cron → harness.sh
  ↓ git pull --rebase
  ↓ worker (script determinístico Python/shell) executa
  ↓ state-updater.py atualiza STATE.md
  ↓ git commit + push
  ↓ log /var/log/pd-framework/<squad>.log
```

**Regra absoluta:** VPS Master nunca roda agente Claude com tool use. Só scripts determinísticos.

### Interativo (Local Windows + VPS Dev SSH)

```
Felipe abre squads/<area>/
  ↓ Claude carrega CLAUDE.md + STATE.md (cascata)
  ↓ trabalha
  ↓ /fechar-squad → STATE.md + append decisions.md
  ↓ git commit + push
```

STATE.md é o elo entre os dois modos.

---

## 7. Sync git — 3 clones

| Clone | Path | Papel |
|---|---|---|
| Local Windows | `Hub Projetos/pd-framework/` | Felipe interativo |
| VPS Dev `/home/felipe/` | `/home/felipe/pd-framework/` (Fase 7) | Felipe SSH interativo |
| VPS Master | `/opt/pd-framework/` (Fase 7) | Workers determinísticos |

Hub GitHub central: `felipeluissalgueiro/pd-framework` (privado).

Conflito STATE.md → VPS vence (`git checkout --theirs`) + alerta WhatsApp Stevo. VPS escreve **só** em `STATE.md` e `queue/obsidian/`.

Crons fora 09:00–17:30 BRT (madrugada 03-06, antes 08-08:55, noite 18-22). Webhooks Cadência podem escrever a qualquer hora.

Detalhes: `pd-framework/docs/git-sync-strategy.md`.

---

## 8. VPS — papéis confirmados (snapshot 25/05)

### VPS Master (72.60.4.71)
- 17 containers Docker (Coolify + Cadência n8n + Lara + Ecuro)
- 4 systemd services PD: grafana-webhook, cadencia-webhook, scoring-webhook, stamper-bot
- /opt/: 8 projetos (master:master)
- Crontab root: 38 entries (pd-marketing, cadência, lara, meta-ads — lançamento Cadência SOAP/wa-broadcast no cron mas **não-operacional**, Felipe confirmou)
- Detalhes: `docs/snapshots/vps-master-2026-05-25.md`

### VPS Dev (2.24.117.172)
- Ubuntu 24.04, node v24.15, python 3.12.3
- **Sem cron, sem systemd customizado** — só ambiente SSH interativo
- /opt/ vazio (só containerd)
- /home/felipe/: Rotina + cadencia-app + pd-portal (3 repos)
- /home/luiz/: cadencia-app + claude-dev-skills + ecuro-mcp + gci-go-whatsapp + pd-portal (5 repos)
- Detalhes: `docs/snapshots/vps-dev-2026-05-25.md`

---

## 9. Credenciais — 1Password Service Account headless

**Setup atual (validado 25/05):** `OP_SERVICE_ACCOUNT_TOKEN` setado em ambiente local. Agentes Claude Code rodam `op item get` **sem prompt de Felipe**.

```bash
op whoami
# URL:               https://my.1password.com

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

# Integration ID:    A3AU24DX3JCURHK2PZRVNDOTJU

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

# User Type:         SERVICE_ACCOUNT

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

```

Mapa real: `Hub Projetos/Credenciais/mapa-1password.md` (consultar sempre antes de `op item get`).

Detalhes: `pd-framework/_core/CREDENTIALS.md`.

**Vazamentos conhecidos (PDL-243 Fase 8):**
1. SA token Grafana — Obsidian nota Stack-Monitoramento (texto limpo 24/05, rotação pendente)
2. `VERCEL_TOKEN` — crontab root VPS Master (rotação pendente)

---

## 10. CLIs, MCPs e APIs

Arquivos no framework com inventário completo + exemplos de uso reais:
- `pd-framework/_core/CLIs.md` — gh, op, vercel, railway, npx supabase, uv/specify, claude/codex/gemini, docker, systemctl, etc + exemplos comando
- `pd-framework/_core/CREDENTIALS.md` — setup SA + comandos op + procedimento rotação
- `pd-framework/_core/MCP-AND-APIS.md` — MCPs CLI (Linear, IDE) vs claude.ai web (Notion, Drive, Gmail, etc) + APIs REST (GHL, Stevo, Supabase, Vercel, Cloudflare, Tally) + exemplos Python/curl

---

## 11. OpenClaw — dois usos distintos

**Não confundir:**

| Uso | Status |
|---|---|
| (a) Motor comercial PD (containers + workers prospecção) | VAI ser depreciado — workers migram pra `squads/comercial/`, container desliga. Sequência: **depois** de evoluir/migrar as Laras |
| (b) Image base das Laras (`openclaw-openclaw` em lara-ceilandia/lara-central) | CONTINUA viva — não há plano de refatorar |

Salvo na memória `project_openclaw_dois_usos.md` (auto-memory Stamper).

---

## 12. Lançamento Cadência — entries cron mas não-operacional

`disparo-soap.py` + `dispatch/wa-broadcast-worker.py` no crontab root da Master (datas 04-29/05) mas Felipe confirmou **não estão funcionando**. NÃO bloqueia migração `/root/pd-marketing/` → `/opt/apps/pd-marketing/` (Fase 2). Entries cron viram input pra Squad Marketing decidir o que reativar/aposentar.

---

## 13. Stack operacional

| Ferramenta | Uso |
|---|---|
| Linear | Issues, sprints, projetos (Felipe + Luiz) |
| Obsidian (Pessoal + Time PD) | Fonte de verdade processos, runbooks, atas, contexto |
| GitHub `Posicionamento-Digital` | Código produto/cliente (cadencia-app, pd-portal, lara-ai, ecuro-mcp, gci-go-whatsapp, insight-artificial) |
| GitHub `felipeluissalgueiro` | pd-framework + rotina + meeting-transcriber + scripts pessoais |
| GHL | CRM, automação cliente |
| Asaas | Cobrança, faturamento |
| N8N | Automações internas Cadência |
| Tally | Formulários |
| Stevo | WhatsApp número pessoal Felipe |
| Coolify | Deploy containers VPS Master |
| Grafana Cloud + Alloy + Loki | Observabilidade |
| 1Password (SA) | Credenciais — fonte única, headless |

---

## 14. Fases de implementação — estado atual

| Fase | Issue | Status | Detalhes |
|---|---|---|---|
| 0 | PDL-218 | ✅ Done | Bootstrap monorepo local (commits affa694 a 759ec89) |
| 0.5 | PDL-219 | Backlog | Reorg pastas externas OneDrive — preenche PATHS.md |
| 0.7 | PDL-241 | ✅ Done | INVENTORY (139 skills) + CONSTITUTION + PERSONAS + DEV-WORKFLOW + REFERENCE-AIOX/BMAD + SKILLS-IMPORT-MAP + DECISIONS-PDL241 |
| 1 | PDL-220 | ✅ Done | Stamper migrado: persona Doug Stamper + 4 context + 56 memory + 17 skills + 2 entry points. 83 arquivos em `stamper/`. Ver [[2026-05-25 Stamper — Chief of Staff PD Framework]] |
| 2 | PDL-221 | Backlog (parent) | Squads operacionais — sub-issues PDL-226..231 |
| 3 | PDL-222 | Backlog (parent) | Squad Produto — sub-issues PDL-232..240 |
| 4 | PDL-223 | Backlog | Auto-fix observabilidade (plano em `docs/plans/fase-4-auto-fix-observabilidade.md`) |
| 5 | PDL-224 | Backlog | Refator skills Linear v2 (depende PROJECT-TYPES.md ✅ refinado) |
| 6 | PDL-225 | Backlog | Framework do Luiz |
| 7 | PDL-242 | Backlog | Clones VPS Dev + VPS Master |
| 8 | PDL-243 | Backlog | **NOVO** — Auditoria final credenciais vazadas + rotação |

Total: 26 issues PDL-218..243.

**Bloqueios externos (não bloqueiam Fase 1+):**
- PDL-213 — mover `/cadencia/` → `/opt/cadencia-growth/` (afeta sub-squad Cadência Growth)
- PDL-215 — env vars Coolify 6 apps (afeta Fase 3 e 6)
- Migração `/root/` → `/opt/apps/` na Master (afeta paths Marketing/CS/Comercial)

---

## 15. Decisões pendentes que afetam fases futuras

1. **`cadencia-webhook` na allowlist Fase 4?** Restart afeta Cadência (produto core). Default sugerido: PROIBIDO ou com `--force` flag obrigatória.
2. **Stevo callback existe?** Endpoint approve Fase 4 depende disso. Confirmar com docs sm-canguru.
3. **STATE.md commit por alerta vs batch?** Webhook + executor podem poluir histórico git.
4. **Bot Telegram Stamper** (`/opt/stamper-telegram-bot/`) — manter ou substituir por sessões interativas?
5. **MCP Ecuro custom** — workaround pra CLI Windows? (relevante quando Squad GCI-GO for populado)
6. **Repo Luiz Fase 6** — `pd-framework-luiz` precisa submodule pra `_shared/`/`_core/`?

---

## 16. Auto-memory Felipe — migra pra stamper/memory/ versionada

Memórias persistentes do Stamper (auto-memory) hoje vivem em:
`~/.claude/projects/C--Users-felip-OneDrive-Documentos-ClaudeCode-Hub-Projetos-Rotina/memory/`

Fase 1 (PDL-220) migra pra `pd-framework/stamper/memory/` (versionada git). Auto-memory hook do harness Claude Code precisa ser adaptado pra apontar pra lá quando cwd é o framework.

Memórias críticas (38+ entradas hoje):
- Perfil profissional Felipe, apelido Stamper, executa não subestimar
- Ritmo cognitivo, blocos por output não tempo
- Anti-burnout, sem trabalho noite, pico criativo não técnico
- Stack ativa, pessoas-chave, cadência comercial
- Framework REP-G, pivot conteúdo builders
- Credenciais nunca texto claro
- Linear Done imediato, WhatsApp confirmação explícita
- OpenClaw dois usos (recém-criada)
- (varias project_*, feedback_*, user_*, reference_*)

---

## 17. Notas Relacionadas (histórico de design)

- [[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]] — sessão design inicial
- [[IA-Tecnologia/2026-05-23 AIOX Core — framework de orquestração de agentes]] — base teórica
- [[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapeamento real de squads e infraestrutura]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapa final e decisões consolidadas]] — era fonte de verdade até 24/05
- [[IA-Tecnologia/2026-05-24 PD Framework — SOUL.md vs CLAUDE.md vs STATE.md]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Estratégia de sync Git VPS e local]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Fase 4 plano técnico (Auto-fix observabilidade)]]
- [[Infra/Stack-Monitoramento-VPS-Master]] — webhook v2 + observabilidade existentes (credenciais limpas 24/05)
