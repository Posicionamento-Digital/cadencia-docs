---
date: 2026-07-07
tags: [documentacao, projeto]
type: source
entities: ["[[PD Framework - Motor Autonomo 247]]", "[[PD Framework]]"]
moc: "[[MOC-Projetos]]"
---
# Motor Autônomo — cascata completa + go-live (07/07/2026)

> Doc viva (fonte da verdade p/ agentes): `_core/MOTOR-AUTONOMO.md` no repo pd-framework. Esta nota é o playbook consultável.

## O que é
Motor pega issues `own:motor` do Linear → worker headless conduz o processo interno do framework (analisa → implementa → auto-revisa → abre PR) → **para na alçada** (nunca mergeia). Roda 24/7 no container `pd-motor` (VPS Dev).

## Go-live validado (07/07)
Cascata completa provada em PRs **reais** do motor: #41 (DEV-1227) e #43 (DEV-1205). O agente moveu o Linear, auto-revisou o próprio código, entregou PR de 6 seções pra revisão humana.

## A cascata (na ordem)
1. **Analisa** — confere critério de aceite; NÃO re-planeja; sem debug-polya.
2. **Implementa** só o escopo.
3. **Valida** — testes/lint; escreve teste se pedido.
4. **AUTO-REVISÃO** — re-lê o próprio diff vs cada critério + corrige buracos ("não deixar nada de fora").
5. **Commita** + escreve `.pd/pr-body.md` (corpo de 6 seções).
6. Launcher: **PR** rico + **In Review** + `own:motor`→`own:review`.
7. Humano aprova via `/aprovar-pr` → **merge + close→Done** (`issue_flow close --approved-externally`).

## Duas filas
- `own:agente` → `autofix_worker` (bug reativo, /15min).
- `own:motor` → **Motor** (trabalho planejado que toma tempo). Dois times, dois propósitos.

## Alçada (regra dura)
Motor roda até o PR. **Nunca mergeia.** Close→Done só após o merge humano.

## Entregas
DEV-1218 (fila own:motor) · DEV-1264 (fix worker no container: settings mínimo portável — hooks path-Windows travavam o headless) · DEV-1265 (cascata + PR rico + own:review) · DEV-1266 (fila-vazia=idle + close --approved-externally + passo 5c do /aprovar-pr).

## Gotchas
codex `-s danger-full-access` (bwrap✗ no container) · `gpt-5.5` (não `-codex`) · git identity no container · hooks do `.claude/settings.json` com path Windows travam o worker → settings mínimo por worktree. Detalhe: memória Stamper `reference-motor-container-gotchas`.

## Falta
DEV-1137 (escalação crítica) · DEV-1221 (multi-repo no container) · budget guard código (DEV-1105) · DEV-1185 (paralelismo).

## Histórico
- 2026-07-07 — go-live + cascata (DEV-1218/1264/1265/1266); doc gerada por /documentar.

## Notas relacionadas
[[PD Framework - Motor Autonomo 247]]
