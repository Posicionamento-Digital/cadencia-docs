---
date: 2026-07-04
tags: [documentacao, projeto, motor-autonomo]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]"]
---
# Motor Autônomo 24/7 — overview do componente

> Doc-índice do Motor Autônomo (epic DEV-1132). Amarra os motores (`motor.py`/`motor_select.py`/`motor_run.py`) com as políticas (`PR-ESCALATION-MATRIX.md`/`BUDGET-GUARD.md`/`MODEL-MAP`). Pra o desenho decisão-a-decisão, ver `decisions.md` (Time Dev, 2026-07-04).

## TL;DR

O motor pega issues marcadas `own:agente` do Linear, resolve o squad dono, lança um Claude headless que codifica sozinho numa worktree isolada, abre PR, e **para na fronteira de alçada** — nunca mergeia produção nem deploya sem humano. Roda na **VPS Dev** (nunca na Master — determinística por `SECURITY.md §1`). Ligado/desligado por um kill switch versionado no git (`default OFF`). MVP **serial**; paralelismo é parâmetro futuro (DEV-1185).

## Identidade

- **Tipo:** orquestrador determinístico + worker agente (Claude headless)
- **Stack:** Python 3.12/3.14 · git (plumbing + worktrees) · Linear GraphQL · `claude -p` headless
- **Path:** `_core/motor*.py` + `_core/PR-ESCALATION-MATRIX.md` + `_core/BUDGET-GUARD.md` + `_core/MODEL-MAP.json`
- **Onde roda:** VPS Dev ou Windows (NUNCA VPS Master — `SECURITY.md §1`, worker é agente com tool-use)
- **Status:** caminho feliz ✅ validado vivo (PR #26); loop driver + auto-merge/escalação em construção

## Componentes internos

| Arquivo | Papel | Estado |
|---|---|---|
| `_core/motor.py` | **Kill switch.** `on/off/status/check` + skill `/motor`. Estado na branch git `motor-state` (propaga por fetch), **default OFF fail-safe**, `is_enabled()` checado a cada iteração. Auditoria: autor+motivo+timestamp por toggle (DEV-1182) | ✅ e2e |
| `_core/motor_select.py` | **Seleção + claim.** Fila = label `own:agente` em backlog/unstarted, ordenada por prioridade (P1→P4). Gate `is_enabled` primeiro → colisão via `linear_claims` (não pega issue de dono ativo) → squad via `squad_resolver` → modelo/effort via `MODEL-MAP motor_selector` → claim (DEV-1134) | ✅ e2e |
| `_core/motor_run.py` | **Caminho feliz.** 1 ciclo: seleção → worktree isolada + branch → run headless (`claude -p`, guards ativos, env limpo do gateway → auth de assinatura) → launcher determinístico faz PR + In Review + comentário + outcome. Sem commits → release gracioso. NUNCA merge/deploy/main (DEV-1135) | ✅ e2e (PR #26) |
| `_core/PR-ESCALATION-MATRIX.md` | **Política de alçada** (quem aprova o quê) + coordenação (colisão humano×agente) | doc |
| `_core/BUDGET-GUARD.md` | **Freios** de $ (tiers→free) e esforço (pit-stop) | doc |
| `_core/MODEL-MAP.json → motor_selector` | **Seletor de modelo+effort** por issue (piso sonnet pra código) | doc |
| `_core/linear_claims.py` | check/claim/release de issue (reusado pela seleção) | ✅ |

## Como funciona (fluxo de 1 ciclo)

1. **Gate:** `motor.is_enabled()` (fresh). OFF → nada acontece. Checado a CADA iteração.
2. **Seleção:** fila `own:agente` por prioridade → pula quem tem dono ativo (colisão) → resolve squad → escolhe modelo/effort → **clama** (assignee + In Progress + comentário).
3. **Isolamento:** worktree própria (`.claude/worktrees/motor-<id>`, junction fora do OneDrive — DEV-865) + branch `feat/<id>` de `origin/main`.
4. **Trabalho:** `claude -p --model X --effort Y` headless, prompt ESTREITO (só coda e commita; guards PreToolUse ativos bloqueiam o proibido). Env limpo das vars de gateway pago → autentica pela assinatura.
5. **Entrega:** houve commit → launcher faz push + **PR** (via `gh`) + move **In Review** + comenta com link + registra outcome. Sem commit → **release** com motivo. O deploy/merge NUNCA é do motor.
6. **Assíncrono:** PR aberto = "aguardando alçada". O motor **não espera** — pega a próxima issue. Aprovação chega depois pela aba Reviews do Linear.

## Decisões (todas 2026-07-04, guiadas com Felipe)

- **Alçada por nível org** (agente/Luiz/CTO), auto-merge só em `feature/*` — `PR-ESCALATION-MATRIX.md`
- **Aprovação assíncrona não-bloqueante** + aba Reviews do Linear como canal
- **Colisão** → agente pausa aquela issue e vai pra outra
- **Budget** duplo ($ tiers→free; esforço pit-stop) — `BUDGET-GUARD.md`
- **Piso de modelo = sonnet** pra qualquer código (haiku não coda) — `MODEL-MAP`
- **Kill switch** default OFF, git-versionado
- **Serial no MVP**, paralelismo por squad = DEV-1185

## Quando NÃO usar / limites

- **Nunca na VPS Master** (determinística).
- **Nunca mergeia prod, deploya, force-push, mensagem a cliente** (classe Proibido da matriz) — mão humana.
- Só pega issue **explicitamente** marcada `own:agente` — não varre o backlog inteiro.

## Quickstart

```bash
python _core/motor.py status              # ligado/desligado?
python _core/motor.py on --reason "..."    # liga (ou skill /motor)
python _core/motor_select.py queue         # o que está na fila do motor
python _core/motor_run.py run --dry-run     # simula 1 ciclo sem executar
python _core/motor_run.py run               # 1 ciclo real (worktree→worker→PR)
python _core/motor.py off --reason "..."    # kill switch
```

## Don'ts

- NUNCA rodar o worker (agente) na VPS Master.
- NUNCA deixar o motor mergear em `main`/produção (classe trivial só auto-mergeia em `feature/*`).
- NUNCA `git add -f` dentro de `.claude/skills` (quebra a junction — incidente 2026-07-04).
- O worker herda env: se rodar num ambiente com `ANTHROPIC_BASE_URL` de gateway, o `motor_run` já strippa — não reintroduzir.

## Falta construir

DEV-1136 (auto-merge classe trivial em `feature/*`) · DEV-1137 (escalar crítico WhatsApp/Slack + pausar) · **loop driver** (capstone DEV-1132: `run_cycle` em loop + deploy cron/service na VPS Dev) · budget guard código (DEV-1105) · DEV-1185 (paralelismo).

## Refs

- `_core/PR-ESCALATION-MATRIX.md` · `_core/BUDGET-GUARD.md` · `_core/MODEL-MAP.json`
- `times/dev/memory/decisions.md` (2026-07-04 — 6 blocos de decisão do motor)
- Canvas visual: `Obsidian_Vaults_Empresa/Projetos/PD Framework - Motor Autonomo 247/escalation-matrix.canvas`
- Epic `DEV-1132` · stories `DEV-1133/1134/1135/1136/1137/1182/1185` · `DEV-1105` (budget) · `SECURITY.md §1`


## Conexoes
- [[Projetos/PD Framework - Motor Autonomo 247/escalation-matrix.canvas]] (Canvas do sistema)
- Epic DEV-1132
