---
date: 2026-05-25
tags: [ia, framework, pd, time, infra]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Time infra

> Documentação humana do bootstrap. Fonte canônica: `pd-framework/times/infra/`
> Linear: [PDL-257](https://linear.app/posicionamento-digital/issue/PDL-257) (refator pós-Modo Foco) · [PDL-226](https://linear.app/posicionamento-digital/issue/PDL-226) (bootstrap original)
> Commit: `c379a06` (refator) · `b1dbbee` (rename squads/→times/)

## Função do Time

Operação de infraestrutura da PD: acesso e hardening das VPS (Master = produção, Dev = interativo), observabilidade (Grafana + Loki + Alloy + webhook v2 → WhatsApp Stevo + Linear), deploy infra (Coolify + Traefik + Cloudflare), DNS, certificados SSL, backup/disaster recovery (em revisão — não automatizado hoje), auto-fix de incidentes (runbook-executor PDL-223), setup de novo cliente em VPS (deploy keys + clone). **Não faz código de produto**, não opera workers de marketing/comercial/cs (esses pertencem aos Squads donos — Infra só dá suporte na VPS).

## Estrutura

```
times/infra/
├── CLAUDE.md (persona: Diego — DevOps + SecOps acumulado)
├── foundation/ (6 docs constitutivos)
│   ├── README.md
│   ├── security-principles.md     (8 princípios consolidados)
│   ├── runbook-overview.md        (formato H3 + exit codes 0/2/3/4/≥10)
│   ├── allowlist-policy.md        (deny-by-default, snapshot 5+2 permitidos / 8 proibidos)
│   ├── monitoring-stack.md        (Grafana+Alloy+Loki+webhook v2 + 7 alert rules)
│   └── backup-recovery.md         (EM REVISÃO — sem backup automatizado hoje)
├── skills/ (6 skills)
│   ├── vps-master/SKILL.md
│   ├── vps-dev/SKILL.md
│   ├── espelhar-repo-vps/SKILL.md
│   ├── validar-deploy-vps/SKILL.md
│   ├── conectar-vps/SKILL.md
│   └── infra-debate.md            (party mode — 5 lentes Diego ou cross-Time Vitor)
├── memory/
│   ├── STATE.md                   (L1 status / L2 progresso / L3 Onboarding)
│   └── decisions.md               (append-only, mais recente em cima)
├── context/
│   ├── topologia-vps.md           (snapshot Master + Dev)
│   └── alert-rules.md             (7 rules + thresholds + PromQL/LogQL)
├── runbooks/
│   ├── ALLOWLIST.md               (regra absoluta deny-by-default)
│   └── {disco,load,ram,security,tcp,traefik,vercel}/  (stubs — PDL-223 Fase 4 popula)
└── workers/
    ├── crons/schedule.yaml
    └── legacy/README.md           (3 ponteiros: monitor-vps.sh, collect-custom-metrics.py, webhook-receptor.py)
```

**Sem sub-squads.** Monolítico — Felipe único operador + Diego única persona. Promove pra sub-squads (`security/`, `observability/`, `deploy/`) quando auto-fix engine PDL-223 trouxer agentes especializados.

## Personas

| Persona | Squad | Inspiração | Voz |
|---|---|---|---|
| **Diego** | Time Infra (líder + única) | AIOX devops | DevOps + SecOps acumulado. Pragmática, conservadora com produção, ALLOWLIST first, deny-by-default |

**Critério pra separar SecOps:** quando PDL-243 (auditoria credenciais) acumular >2 vazamentos/mês, abrir `/criar-squad` pra promover SecOps a persona dedicada. Hoje (2 vazamentos totais) volume não justifica.

**Cross-Time invocável:** Vitor (Dev Tech Lead) chamado em `/infra-debate` quando tema toca arquitetura de aplicação (deploy strategy, container choice, performance, integração com produto).

## Foundation docs (com status)

| Doc | Status | Conteúdo principal |
|---|---|---|
| `security-principles.md` | ✅ populado | 8 princípios: VPS Master determinística, ALLOWLIST first, 1P fonte única, janela cron 09-17:30 zona exclusão, push main com pre-commit, ops destrutivas confirmação textual, VPS Master só escreve STATE+queue, knowledge lookup pré-classificada |
| `runbook-overview.md` | ✅ populado | Categorias por alert (disco/load/ram/security/tcp/traefik/vercel); critério promoção ação→runbook (6 itens); formato H3 4-seções; exit codes padronizados; fluxo runbook-executor |
| `allowlist-policy.md` | ✅ populado | Snapshot 5 containers + 2 systemd permitidos / 8 categorias proibidas; critério promoção 6 itens; critério exclusão 3 itens; processo PR + revisão Felipe |
| `monitoring-stack.md` | ✅ populado | Grafana Cloud `felipeluissalgueiro.grafana.net` + Alloy + Loki + webhook v2 porta 9300; 7 alert rules; métricas custom textfile; dedup fingerprint TTL 30min; vazamentos PDL-243 |
| `backup-recovery.md` | ⚠️ EM REVISÃO | Não existe backup automatizado VPS Master hoje. Estado atual + plano detalhado (RTO/RPO/script/cron/retention/monitoring/restore drill). Aponta para PDL-258 (implementação) |
| `naming-conventions.md` | ❌ ADIADO | Convenções já implícitas em `context/topologia-vps.md` (containers `cadencia-*`/`lara-*`/`ecuro-*`, services `*-webhook`, paths `/opt/<projeto>/`). Formaliza quando 2º agente Infra entrar |
| `incident-response.md` | ❌ ADIADO | Precisa `runbook-overview` consolidado + alinhamento sessão PDL-223 (auto-fix observabilidade). Cria em sessão dedicada |

## Decisões chave (top 5 do decisions.md)

- **2026-05-25 — Refator Time Infra pós-Modo Foco (PDL-257)** — adiciona foundation/+persona Diego formalizada+/infra-debate, refatora STATE L3 pra Onboarding, migra 4 entradas históricas pra decisions.md em formato estruturado (Contexto/Decisão/Alternativas/Impacto/Quem decidiu). Estrutura monolítica (sem sub-squads).
- **2026-05-25 — Squad Infra bootstrap + ALLOWLIST inicial (PDL-226)** — primeiro Squad operacional populado. ALLOWLIST com 5 containers permitidos + 8 categorias proibidas (deny-by-default).
- **2026-05-24 — Snapshots VPS Master + VPS Dev capturados** — baseline auditável em `docs/snapshots/vps-master-2026-05-25.md` + `docs/snapshots/vps-dev-2026-05-25.md`.
- **2026-05-24 — Webhook v2 reconfigurado** — rotulação por squad via `labels.ruleGroup`, dedup fingerprint TTL 30min em `alert_cache.json`, saída dupla WhatsApp Stevo + Linear (label `auto-fix`).
- **2026-05-22 — VPS Master reconfigurada do zero** — user `master` (sudo OK), root SSH disabled, SSH hardening, UFW + Cloudflare allowlist, Coolify 4.1.0, Traefik v3.3.5, projetos migrados pra `/opt/<projeto>/`.

## Pessoas-chave

- **Felipe** — operação, único decisor estratégico
- **Luiz** — consumer VPS Dev (escopo limitado: `cadencia-app` + `pd-portal` em `/home/luiz/`)
- **Diego** — persona-agente (DevOps + SecOps acumulado), não pessoa real
- **Hostinger support** — referência operacional pra escalation hardware/rede (registrar em runbook futuro se precisar)

## Projetos Linear vinculados

- **PDL-223** — Central de Observabilidade + Auto-correção com IA — 🟡 In Progress (Fase 4 = runbook-executor consome `runbook-overview.md` + `allowlist-policy.md`)
- **PDL-242** — Migração VPS produção (sair do root + containerizar Claude CLI) — ✅ Done. Fase 7 (deploy pd-framework na VPS) pendente.
- **VPS de Desenvolvimento — Luiz** — ✅ Done
- **PDL-257** — Refator Time Infra pós-Modo Foco — ✅ Done (commit `c379a06`)
- **PDL-258** — Implementar backup automatizado VPS Master — 🔵 Backlog
- **PDL-259** — Criar skill `/rotacionar-credencial` — 🔵 Backlog
- **PDL-260** — Criar skill `/hardening-check` — 🔵 Backlog
- **PDL-261** — Criar skill `/restart-container` — 🔵 Backlog
- **PDL-243** — Auditoria credenciais (2 vazamentos mapeados) — 🟡 In Progress
- **PDL-248** — Gotchas auto-detect por squad — 🟡 In Progress (destravada por este Squad existir)

Mapeamento cascata: `_core/linear-squad-map.json` (3 projetos). Label workspace: `squad:times/infra`.

## Bloqueios externos

- **PDL-242 Fase 7** — deploy `pd-framework` na VPS pendente (bloqueia cron noturno state-aggregator PDL-252)
- **PDL-243** — 2 vazamentos credencial pendentes: SA Grafana (texto removido Obsidian 24/05, rotação pendente) + `VERCEL_TOKEN` crontab root (mover pra `.env` + rotacionar)
- **PDL-252** — cron noturno state-aggregator depende PDL-242 Fase 7
- **PDL-213** — mover `/cadencia/` → `/opt/cadencia-growth/` (afeta Squad Produto/Cadência Growth)
- **Migração `/root/` → `/opt/apps/`** na Master (afeta paths Marketing/CS/Comercial)
- **PDL-215** — env vars Coolify 6 apps
- **Backup automatizado VPS Master inexistente** (PDL-258) — risco real, sem fallback se volume corromper

## Como usar

- **Abrir:** `/abrir-squad times/infra`
- **Debate:** `/infra-debate` (3 modos: reflexão solo 5 lentes Diego, cross-Time com Vitor, ou revisitar quando 2ª persona Infra existir)
- **Antes de operação sensível:** `python pd-framework/_core/lookup.py "<keywords>" --source incidents`
- **Skills:**
  - `/vps-master` — abrir sessão VPS Master (checklist + varredura)
  - `/vps-dev` — abrir sessão VPS Dev (clone/checkout + revisão dev)
  - `/conectar-vps` — genérico (SSH + executa comando remoto)
  - `/espelhar-repo-vps` — provisiona deploy key SSH ed25519 + clone autenticado
  - `/validar-deploy-vps` — checklist pós-deploy (compile + dry-run + crontab)
  - `/infra-debate` — party mode

## Pendências pra sessões futuras

- **PDL-258** — implementar backup automatizado VPS Master (sair do EM REVISÃO no `foundation/backup-recovery.md`)
- **PDL-259/260/261** — escopo dedicado pras 3 skills do backlog
- **PDL-223 Fase 4** — runbook-executor real (popular stubs `runbooks/{disco,load,ram,security,tcp,traefik,vercel}/`)
- **PDL-243** — rotacionar SA Grafana + VERCEL_TOKEN (manual ou via PDL-259 quando nascer)
- **`naming-conventions.md`** + **`incident-response.md`** — foundation docs adiados, criar sob demanda
- **Promover `/infra-debate`** pra debate multi-voz quando 2ª persona Infra existir
- **Revisitar persona única Diego** quando PDL-243 acumular >2 vazamentos/mês

## Notas relacionadas

- [[IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Fase 4 plano técnico (Auto-fix observabilidade)]] — PDL-223 que consome foundation/runbook-overview + allowlist-policy
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapa final e decisões consolidadas]]
- [[Infra/2026-05-25 Time Infra — Estrutura PD Framework (refator PDL-257)]] — playbook operacional irmão (mesma sessão)
- [[Infra/Stack-Monitoramento-VPS-Master]] — doc técnica detalhada webhook v2
- [[Marketing-PD/2026-05-25 Time Marketing — Decisões de Bootstrap]] — Time-modelo (referência paralela)
