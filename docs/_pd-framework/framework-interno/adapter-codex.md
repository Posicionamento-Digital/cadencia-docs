---
date: 2026-07-02
tags: [doc, documentacao, projeto, pd-framework]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]"]
---
# Adapter Codex (#3) — Runtime Contract

## Identidade
- **Tipo:** adapter de runtime (hooks nativos + shims Python)
- **Stack:** Python 3.14 · codex-cli ≥ 0.142.5 (feature `hooks` stable)
- **Path no repo:** `adapters/codex/` + `.codex/hooks.json` + `AGENTS.md` raiz
- **Status:** ativo — **validado e2e sob `codex` real em 2026-07-02** (DEV-1053/DEV-1099 Done)

## O que é
Terceiro adapter do Runtime Contract do pd-framework (depois de #1 Claude Code e #2 OpenCode). Faz o Codex CLI operar o framework com paridade das capacidades C1–C8: contexto por cwd, routing de squad, branch de sessão, proteção da main, scan de credencial, merge automático no encerramento, skills e knowledge lookup.

## Para que serve
Rodar o framework em runtime que não é o Claude Code sem perder as garantias de lifecycle e segurança — mesma main protegida, mesma memória, mesmos scripts do core (`_core/runtime/*`). O adapter é casca fina: traduz o payload dos hooks do Codex e faz shell-out pros mesmos scripts que os adapters #1/#2 usam.

## Como funciona
1. `.codex/hooks.json` mapeia os 5 eventos (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop) pra shims em `adapters/codex/`.
2. Escrita na main → `PreToolUse` nega via JSON `permissionDecision:"deny"` → agente cria `session/*` com escalonamento (sandbox não deixa o hook tocar o `.git`) → re-executa.
3. `PostToolUse` é rede de segurança (garante branch) + record_memory; `Stop` auto-commita e mergeia a sessão na main.

## Quickstart
```bash
codex features enable hooks
python adapters/codex/bootstrap.py      # regenera hooks.json (python local) + persiste trust
python adapters/codex/sync_skills.py    # expõe skills no /skill
codex                                    # hooks disparam confiados, sem flag
```

## Decisões (principais)
- **Bloqueio via JSON deny, nunca exit 2** — na 0.142.5 Windows, exit 2 + stderr é fail-open na prática (contradiz a doc oficial). Validado por experimento isolado.
- **`command` sem aspas** — o spawn via `cmd.exe /C` quebra com aspas escapadas pelo Rust; hooks morriam silenciosamente (fail-open).
- **Trust por edição direta do `config.toml`** — o bootstrap replica o hash `version_for_toml` (sha256 do JSON canônico), contornando o bug openai/codex#22847 do `/hooks`.
- Histórico completo: `times/dev/memory/decisions.md` (2026-06-30 → 2026-07-02).

## Don'ts
- Nunca voltar o `deny()` pra exit 2 "porque a doc diz que funciona" — não funciona nesta versão.
- Nunca adicionar aspas nos `command` do `hooks.json`.
- Nunca rodar Claude Code e Codex no mesmo working tree — os hooks de session-branch dos dois embaralham o `.git`.
- Hook nunca pode sair sem drenar o stdin (fail-open por "failed to write hook stdin").

## Troubleshooting
- **`hook: <evento> Failed` e a tool executa** → hook não spawnou (aspas/path) OU exit ≠ 0 sem JSON. Rodar `python adapters/codex/bootstrap.py` e conferir o smoke.
- **Hooks não disparam de jeito nenhum** → `codex features list` (hooks = true?) + trust: re-rodar o bootstrap (re-hash) — editar `hooks.json` invalida o `trusted_hash`.
- **`codex exec` pendura em script** → stdin-pipe aberto; usar `</dev/null` e `-C <dir>`.
- **Smoke:** `python adapters/codex/run_smoke.py` (45 testes, gate de release).

## Histórico
- 2026-07-01 — 9 stories implementadas (DEV-1009…1020), smoke verde, mas hooks não rodavam no codex real (python stub, flag, sandbox)
- 2026-07-02 — e2e final PASSOU em clone isolado; 2 causas raiz corrigidas (aspas no spawn + exit 2 fail-open → JSON deny); `bootstrap.py` criado (DEV-1099); trust persistido sem `/hooks`; DEV-1053 e DEV-1099 Done

## Notas Relacionadas
[[PD Framework]] · [[Projetos/PD Framework/Docs/2026-05-25 PD Framework - Estrutura Completa Fase 0 Inventário e Decisões]]
