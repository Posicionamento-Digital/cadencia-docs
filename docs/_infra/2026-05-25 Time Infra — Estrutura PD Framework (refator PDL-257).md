---
date: 2026-05-25
tags: [pd, infra, framework, playbook]
moc: "[[Infra]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]", "[[Central de Observabilidade]]", "[[PD Framework]]", "[[comercial]]", "[[marketing]]"]
---
# Time Infra — Estrutura PD Framework (pós-refator PDL-257)

> Playbook de referência operacional do Time Infra no [[../IA-Tecnologia/2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada|PD Framework]]. Consultar antes de abrir Squad Infra ou tomar decisão estrutural.

Repo: `pd-framework/times/infra/` · Commit refator: `c379a06` · Issue: PDL-257 Done.

---

## TL;DR

Time Infra refatorado em 2026-05-25 (PDL-257) pra alinhar com padrão pós-Modo Foco (igual Marketing/Comercial/Dev). Monolítico (sem sub-squads). Persona única: **Diego** (DevOps + SecOps acumulado até demanda justificar separação). Foundation com 5 docs constitutivos + 1 EM REVISÃO. Skill nova: `/infra-debate` (reflexão 5 lentes ou cross-Time com Vitor).

---

## Estrutura final

```
times/infra/
├── CLAUDE.md                  ← persona Diego + escopo + foundation refs
├── memory/
│   ├── STATE.md               ← L1 status / L2 progresso / L3 Onboarding
│   └── decisions.md           ← append-only, mais recente em cima
├── foundation/                ← docs constitutivos (consultar ANTES de operar)
│   ├── README.md              ← índice + regra consulta obrigatória
│   ├── security-principles.md ← VPS Master determinística, ALLOWLIST first, 1P fonte única, janela cron, push direto main com pre-commit
│   ├── runbook-overview.md    ← índice runbooks + critério criação + formato H3 + códigos saída padronizados
│   ├── allowlist-policy.md    ← deny-by-default, critério promoção/exclusão, processo PR + revisão Felipe
│   ├── monitoring-stack.md    ← Grafana Cloud + Alloy + Loki + webhook v2 + 7 alert rules (arquitetura completa)
│   └── backup-recovery.md     ← EM REVISÃO (sem backup automatizado hoje — PDL-258)
├── context/
│   ├── topologia-vps.md       ← snapshot Master + Dev (refresh quando mudar)
│   └── alert-rules.md         ← 7 rules ativas + threshold + PromQL/LogQL
├── runbooks/
│   ├── ALLOWLIST.md           ← regra absoluta deny-by-default (5 permitidos + 8 proibidos)
│   ├── disco/  load/  ram/  security/  tcp/  traefik/  vercel/    ← stubs (PDL-223 Fase 4 popula)
├── skills/
│   ├── vps-master/SKILL.md
│   ├── vps-dev/SKILL.md
│   ├── espelhar-repo-vps/SKILL.md
│   ├── validar-deploy-vps/SKILL.md
│   ├── conectar-vps/SKILL.md
│   └── infra-debate.md        ← NOVO (party mode adaptado, modelo marketing-debate)
└── workers/
    ├── crons/schedule.yaml
    └── legacy/README.md       ← ponteiros pros 3 workers VPS atuais
```

---

## Foundation — o que cada doc cobre

| Doc | Quando ler | Resumo |
|---|---|---|
| `security-principles.md` | Tocar credencial, deploy, push main, qualquer operação em produção | 8 princípios: VPS Master determinística; ALLOWLIST first; 1P fonte única; janela cron 09-17:30 BRT zona exclusão; push main com pre-commit + review; ops destrutivas exigem confirmação textual; VPS Master só escreve STATE.md e queue/obsidian/; knowledge lookup antes de classificada |
| `runbook-overview.md` | Criar runbook novo, debugar runbook-executor | Estrutura categorias (disco/load/ram/security/tcp/traefik/vercel); critério promoção ação→runbook; formato H3 4-seções; exit codes 0/2/3/4/≥10; fluxo runbook-executor |
| `allowlist-policy.md` | Adicionar/remover container da ALLOWLIST | Snapshot atual (5 permitidos: coolify-proxy/sentinel/realtime/insight-artificial/assessoria-imprensa-cadencia + 2 systemd: grafana-webhook/scoring-webhook); critério promoção 6 itens; critério exclusão 3 itens; processo PR + revisão Felipe + entrada decisions.md |
| `monitoring-stack.md` | Mexer em alert rule, webhook, métrica customizada | Diagrama lógico stack (Alloy → Loki + Prometheus; webhook v2 → WhatsApp + Linear); Grafana Cloud `felipeluissalgueiro.grafana.net`; 7 alert rules; métricas custom (`traefik_memory_bytes`, `tcp_close_wait_total`, `vercel_deploy_failed`); webhook v2 fluxo + dedup fingerprint TTL 30min |
| `backup-recovery.md` | **EM REVISÃO** — implementar (PDL-258) | Estado atual: sem backup automatizado. 3 Postgres (cadencia/coolify/ecuro) + volumes Docker sem snapshot. Plano: pg_dump + tar → S3-compat (B2/R2), cron 03:30, retention 7-4-6, alert "backup-stale", restore drill trimestral |

---

## Persona Diego

**DevOps + SecOps acumulado.** Origem AIOX devops. Voz: pragmática, conservadora com produção, ALLOWLIST first.

**Princípios não-negociáveis** (espelham [[../IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times|Constituição]] §regras absolutas):
- NUNCA `git push --force` em main
- NUNCA deploy em janela proibida (09-17:30 BRT)
- SEMPRE backup antes de destrutivo em VPS
- VPS Master = só scripts determinísticos. Nunca agente Claude com tool use lá
- ALLOWLIST first. Tudo que não está listado em `runbooks/ALLOWLIST.md` = proibido

**Critério de revisita pra separar SecOps:** quando PDL-243 (auditoria credenciais) acumular >2 vazamentos/mês, abrir `/criar-squad` pra promover SecOps a sub-squad ou persona dedicada. Hoje (2 vazamentos totais) volume não justifica.

---

## Como operar

### Abrir sessão de trabalho

```
/abrir-squad times/infra
```

Carrega CLAUDE.md (persona Diego + escopo + foundation refs) + STATE.md (situação agora). Foundation docs são consultados **sob demanda** quando operação relevante surge (não pré-carregados).

### Debate / decisão difícil

```
/infra-debate

Tema: <descrever>
Modo: reflexão solo (5 lentes Diego) | cross-Time (Diego + Vitor)
```

**5 lentes Diego solo** (forçar análise por ângulo):
- Segurança · Observabilidade · Operação · Custo · Deploy

**Cross-Time com Vitor** (Dev Tech Lead invocado quando tema toca arquitetura de aplicação):
- Deploy strategy, container choice, performance, integração com produto
- Tensão produtiva: Vitor puxa design limpo, Diego puxa operação simples

### Antes de operação sensível

```bash
python pd-framework/_core/lookup.py "<keywords>" --source incidents
```

Cobre incidents (Hub) + sessions + memory + gotchas. Obrigatório antes de deploy / DNS / SSL / destrutivo / debug de bug novo / tocar área com histórico.

### Fechar sessão

```
/fechar-squad times/infra
```

Atualiza STATE.md + append decisions.md se houve decisão + commit + push + propaga L1 pro Time pai (no caso infra é top-level, propagação N/A).

---

## Issues Linear ativas

| Issue | Título | Status | Notas |
|---|---|---|---|
| **PDL-257** | Refator Time Infra pós-Modo Foco | ✅ Done | Closes via commit c379a06 (2026-05-25) |
| **PDL-258** | Implementar backup automatizado VPS Master | 🔵 Backlog | Promove quando priorizar — sem backup hoje é risco real |
| **PDL-259** | Criar skill /rotacionar-credencial | 🔵 Backlog | Útil pra PDL-243 (rotacionar SA Grafana + VERCEL_TOKEN) |
| **PDL-260** | Criar skill /hardening-check | 🔵 Backlog | CIS Benchmarks aplicado Master + Dev |
| **PDL-261** | Criar skill /restart-container | 🔵 Backlog | Wrapper com check ALLOWLIST integrado |
| **PDL-223** | Central de Observabilidade + Auto-correção com IA | 🟡 In Progress | Fase 4 = runbook-executor (consome `runbook-overview.md` + `allowlist-policy.md`) |
| **PDL-243** | Auditoria credenciais | 🟡 In Progress | 2 vazamentos mapeados (SA Grafana + VERCEL_TOKEN) |
| **PDL-248** | Gotchas auto-detect por squad | 🟡 In Progress | Depende deste Squad existir ✅ |

Label workspace: `squad:times/infra` (criada 2026-05-25, aplicada nas 5 novas).

---

## Bloqueios externos ativos

- **PDL-242 Fase 7** — deploy `pd-framework` na VPS pendente (bloqueia cron noturno state-aggregator PDL-252)
- **PDL-243** — 2 vazamentos credencial pendentes: SA Grafana (texto removido Obsidian 24/05, rotação pendente) + `VERCEL_TOKEN` crontab root (mover pra `.env` + rotacionar)
- **PDL-252** — cron noturno state-aggregator depende PDL-242 Fase 7
- **PDL-213** — mover `/cadencia/` → `/opt/cadencia-growth/` (afeta Squad Produto/Cadência Growth)
- **Migração `/root/` → `/opt/apps/`** na Master (afeta paths Marketing/CS/Comercial — conferir antes de mexer)
- **PDL-215** — env vars Coolify 6 apps
- **Backup automatizado VPS Master inexistente** (PDL-258) — virar bloqueio formal quando promovido pra plano de execução

---

## Decisão central do refator

**(a) — Refatorar L3 do STATE pra Onboarding + mover histórico pra decisions.md**

Razões (registradas em `times/infra/memory/decisions.md` entrada 2026-05-25 PDL-257):
1. Schema oficial pós-2026-05-25 é "L3 = Onboarding" (Marketing/Comercial/Dev seguem)
2. `decisions.md` é exatamente pra histórico durável append-only
3. Os 6 itens originais em L3 ERAM decisões técnicas (webhook v2, ALLOWLIST, snapshots) — formato decisões
4. Consistência cross-Time: `/abrir-squad` em qualquer Time recebe onboarding em L3

**Sub-squads:** monolítico (sem sub-squads) — Felipe é único operador, Diego é única persona. Promove quando auto-fix engine PDL-223 trouxer agentes especializados.

---

## Notas Relacionadas

- [[Stack-Monitoramento-VPS-Master]] — doc técnica detalhada webhook v2 (credenciais já limpas 24/05)
- [[../IA-Tecnologia/2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada]]
- [[../IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- [[../IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]
- [[../IA-Tecnologia/2026-05-25 PD Framework — Fase 4 plano técnico (Auto-fix observabilidade)]] — PDL-223
- [[../Marketing-PD/2026-05-25 Time Marketing — Decisões de Bootstrap]] — modelo de Time refatorado (foundation/ + persona + skill debate)
- [[VPS-Hostinger/VPS-Dev/POP-Uso-VPS-Dev]]
- [[VPS-Hostinger/VPS-Dev/Acesso-VPS-Dev-Luiz]]
