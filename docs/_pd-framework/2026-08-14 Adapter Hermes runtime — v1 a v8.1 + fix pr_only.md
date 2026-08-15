# 2026-08-14 — Adapter Hermes runtime autônomo: v1 → v8.1 + fix hook `on_session_finalize` pr_only

> Sessão-maratona de desenvolvimento do adapter Hermes rodando issues Linear autônomamente no Dell notebook via cascata canônica do PD Framework. Fecha o loop iniciado em 2026-08-13 com a criação da skill `/planejar-fila-hermes` — passou por 8 iterações do prompt+lessons até chegar ao modelo funcional (v8.1) que shipou 7 issues em 1h35min. Ao final, gap arquitetural corrigido: adapter agora emite PR draft por default (`trust_tier="pr_only"`) em vez de merge direto em main.

---

## TL;DR

- **Skill `/planejar-fila-hermes`** funcional: Felipe cura fila em `.pd/hermes-queue.json` + label `own:hermes` + commit/push; Hermes no Dell puxa e processa via cascata canônica.
- **Warm secrets cache Windows** (`warm_secrets.py` + `warm-op-env.ps1`): mata rate limit persistente do 1P que travava sessões cross-ambiente (padrão POSIX já existia via DEV-1347, agora estendido).
- **Padrão do prompt evoluiu em 8 iterações** (v2 spawn recursivo → v3 zerou fila → v4 pulou por heurística → v5 esqueceu Telegram → v6 silent failure em fix → v7 shell direto ignorando skills → v7.1 recriou PR fechado → v8 gpt-5.6-terra bug V4A → **v8.1 gpt-5.5 funcional**). Cada rodada documentada em `lessons-learned.md` (8 lições).
- **3 camadas de reforço** ativas: prompt v8 + `lessons-learned.md` + `AGENTS.md §Adapter #4` (auto-injetado).
- **Hook `on_session_finalize` completo** em `adapters/hermes/hook.py`: agora emite PR draft via `close_session.py --trust-tier pr_only` (era `auto_main` default → merge direto em main sem revisão).
- **8 issues shipadas em main** — DEV-1707 (aprovada antes) + DEV-1714..1720 (via Hermes v8.1).
- **Modelo Hermes atual: gpt-5.5** — revertido de gpt-5.6-terra por bug do validador V4A que rejeitava patches sem modificar arquivos.

## Artefatos criados/alterados

### Novos

| Arquivo | Papel |
|---|---|
| `stamper/skills/planejar-fila-hermes/SKILL.md` | Skill nova (via `python _core/new_skill.py`). Top 10 candidatas + Felipe marca por números + grava fila + commit/push + trigger opcional |
| `stamper/skills/planejar-fila-hermes/prompt-hermes.md` | Prompt versionado entregue ao Hermes (evoluiu v2→v8.1 documentado em lessons) |
| `stamper/skills/planejar-fila-hermes/lessons-learned.md` | 8 rodadas de erros reais com regras duras pra evitar |
| `_core/HERMES-TRIGGER.md` | Fonte única do comando pra disparar Hermes one-shot no Dell |
| `_core/warm_secrets.py` | Motor Python: lê `SECRETS-1P-MAP.json` → escreve `op.env` (1 leitura por chave, evita rate limit) |
| `_core/warm-op-env.ps1` | Wrapper Windows idempotente. ASCII-only pra rodar em PowerShell 5.1 legado |
| `.pd/hermes-queue.json` | Fila versionada (whitelist `.gitignore`) — Hermes lê via `git pull` |
| Label Linear `own:hermes` | Workspace-level, cor `#5E7CE2` (azul). Distinta de `own:motor` e `own:agente` |

### Alterados

| Arquivo | Mudança |
|---|---|
| `AGENTS.md` | Nova seção "Adapter #4 — Hermes: regras duras obrigatórias" — auto-injetada pelo Hermes ao iniciar (regra padrão do runtime). Cobre: usar skills canônicas, anti-fabricação evidência, ler PR fechados, Telegram obrigatório, lessons-learned. |
| `_core/SECRETS-PATTERN.md` | Tabela por-plataforma ganhou linha Windows (warm-op-env.ps1). Nova seção "Rate limit 1P — recorrência e mitigação" com histórico dos 2 incidentes (2026-07-16 + 2026-08-13). |
| `_core/DELL-NOTEBOOK-SETUP.md` | §6.2 nova "Cache de secrets" — receita de bootstrap no Dell. |
| `_core/motor_select.py` | Novo profile `hermes` no `candidates_queue` (permite `assignee=felipe` e `tipo:bug`, exclui P1/bloqueadas/own cruzados/sem roteamento/projeto canceled). |
| `_core/runtime/close_session.py` | (Via Hermes v8.1 DEV-1715/DEV-1716) — recover session owners on open, finalize sessions with lock release, consume memory dirty fallback. |
| `adapters/hermes/hook.py` | **v8.1 shipou** handler `on_session_finalize` completo (DEV-1715) + `_post_tool_observer` (DEV-1714). **Fix pós-sessão**: `trust_tier="pr_only"` explícito no body do `close_session` — agora emite PR draft em vez de auto_main merge. |
| `.gitignore` | Whitelist `!.pd/hermes-queue.json` |

### Issues Linear processadas (todas Done)

| Issue | Escopo | Commit em `origin/main` |
|---|---|---|
| DEV-1707 | feat(hermes): abrir sessão e proteger main antes escrita | c2b5c3ff (aprovada v4) |
| DEV-1714 | feat(hermes): registrar memory dirty após escrita | d4ef784d |
| DEV-1715 | feat(hermes): fechar sessão por on_session_finalize | 5dc12191 |
| DEV-1716 | feat(hermes): recuperar sessões interrompidas e concorrentes | f36178b8 |
| DEV-1717 | feat(parity): automatizar wire protocol e falhas adversas | 834146ea |
| DEV-1718 | feat(parity): executar E2E remoto dos quatro adapters | e81a81d4 |
| DEV-1719 | feat(docs): documentar instalação, operação e rollback Hermes | a090d008 |
| DEV-1720 | feat(rollout): ativar adapter Hermes em fases seguras | (merges 1853/1858) |

## Como funciona o fluxo Hermes autônomo

```
Felipe (Galaxy Book)                    Hermes runtime (Dell notebook)
─────────────────────                    ──────────────────────────────
1. /planejar-fila-hermes
   → escolhe 7-10 issues
   → grava .pd/hermes-queue.json
   → aplica own:hermes no Linear
   → commit + push origin/main
   → pergunta: "dá o start?"

2. SSH ao Dell:
   hermes chat --in <worktree>
     --yolo --accept-hooks
     --max-turns 3000
     --model gpt-5.5
     -q "processe fila..."
                                        3. Hermes lê AGENTS.md (auto-injetado)
                                           lessons-learned.md, prompt-hermes.md,
                                           .pd/hermes-queue.json

                                        4. Pra cada issue X:
                                           - gh pr list --state closed --search X
                                             + gh pr view <N> --comments (feedback anterior)
                                           - use skill linear-start-issue X
                                             → branch feat/<x>-slug, In Progress, manifest
                                           - use skill linear-planejar-issue X
                                             → plano técnico rastreável na issue Linear
                                           - codar seguindo plano
                                           - use skill openrouter-review HEAD~N..HEAD
                                             → GLM 5.2 → fallback Qwen se inconsistente
                                             → fix loop (cap 3) se P1/P2
                                           - use skill linear-close-issue X
                                             → issue_flow.py close (4 gates)
                                             → commit "Closes DEV-X"
                                             → adapter hook on_session_finalize DISPARA:
                                               close_session.py --trust-tier pr_only
                                               → push origin/session-branch
                                               → gh pr create draft
                                               → checkout base
                                             → move Linear In Review
                                           - remover DEV-X de .pd/hermes-queue.json
                                           - hermes send --to telegram "✅ DEV-X concluída"

                                        5. Ao final:
                                           - .pd/hermes-queue.json vazia
                                           - Telegram: "🏁 Fila concluída. Processadas: N. PRs: M."
                                           - encerra sessão

6. Felipe recebe Telegram por
   issue + resumo final.
   Aprova via /aprovar-pr em outra
   sessão (list PRs draft →
   claude-review Opus → merge).
```

## Camadas de reforço v8

O adapter Hermes projeta 22 skills canônicas do framework em `skill-bundles/`. Sem reforço no prompt, Hermes tende a usar `git`/`gh` direto (ignorando skills). 3 camadas garantem o uso:

1. **Prompt v8** (passado via `-q "..."`) — impera cascata via skills, proíbe shell direto, exige leitura de comments dos PRs fechados
2. **`lessons-learned.md`** (leitura obrigatória primeira ação) — 8 rodadas de erro documentadas com regra dura por rodada
3. **`AGENTS.md §Adapter #4`** (auto-injetado pelo Hermes, regra padrão do runtime — só desabilita com `--ignore-rules`) — regras duras cross-adapter. **Camada mais robusta** porque não depende do meu prompt

Fase 4 opcional (não implementada): hook bloqueante `pre_tool_call` em `adapters/hermes/hook.py` que intercepta `gh pr create` fora de contexto de skill canônica. Só necessário se v8+ ignorar as 3 camadas acima.

## Fix crítico pós-v8.1 — `trust_tier="pr_only"` default

v8.1 shipou 7 issues **direto em main** (auto_main merge), não em PR. Causa: `_finalize_session` no adapter Hermes passava `session_id` + `cwd` + `infer_from_head=True`, mas **não passava `trust_tier`** → `close_session.py` usava default `auto_main` (merge local + push main).

Fix (1 linha):

```python
body = json.dumps({
    "session_id": sid,
    "cwd": payload.get("cwd") or str(root),
    "infer_from_head": True,
    "trust_tier": "pr_only",   # ← ADICIONADO
})
```

Próxima rodada Hermes vai:
1. Push session branch pra `origin/session/...`
2. Abrir PR draft via `gh pr create --draft`
3. Checkout de volta pra base
4. `main` fica **intacta** até Felipe aprovar via `/aprovar-pr`

Padrão DEV-WORKFLOW §12.4 restaurado: "nunca mergear/deployar direto, status In Review, aprovação humana necessária".

## Modelo Hermes

- **Atual: `gpt-5.5`** (via `openai-codex`)
- **Testado: `gpt-5.6-terra`** — bug do validador V4A rejeitou 2 patches sem modificar arquivos + helper `hermes_tools.read_file` com KeyError em paths relativos no sandbox. Revertido pra 5.5.
- **Config:** `hermes config set model gpt-5.5` (persiste em `C:/Users/claude/AppData/Local/hermes/config.yaml`)

## Status por ambiente (secrets cache)

| Ambiente | Cache | Fonte |
|---|:---:|---|
| VPS Master (Ubuntu) | ✅ systemd EnvironmentFile | Já existia |
| VPS Dev (Ubuntu) | ✅ `/etc/onboarding/op.env` | DEV-1347 (2026-07-16) |
| Coolify workers (container) | ✅ env vars diretas | Já existia |
| Galaxy Book (Windows) | ✅ `~/.pd-hooks/op.env` | Nesta sessão (2026-08-14) |
| Dell notebook (Windows) | ✅ `~/.pd-hooks/op.env` | Nesta sessão (2026-08-14) |
| CAIXA1 (Windows) | ⏳ adiado | Decisão Felipe (workers da CAIXA1 não usam `_shared/secrets` hoje) |

## Métricas do experimento

| Métrica | Valor |
|---|---|
| Rodadas Hermes | v1-v8.1 (10 iterações) |
| Duração total | ~15h |
| Issues Done | 8 (DEV-1707 aprovada + 7 shipadas por v8.1) |
| PRs abertos ao longo do dia | 20+ (a maioria fechada pra refazer) |
| Reviews Opus 4.7 rodados | ~15 (via `/claude-review`) |
| Reviews GLM/Qwen (OpenRouter) | ~10 |
| Camadas de reforço construídas | 3 |
| Lessons documentadas | 8 (spawn recursivo, zerou fila, pulou heurística, esqueceu Telegram, silent failure, shell direto, recriou PR fechado, evidência fabricada) |
| Custo aproximado | ~$0.15 em reviews GLM + tempo Claude Code / Hermes (assinatura) |

## Ganhos permanentes

- Skill `/planejar-fila-hermes` funcional pra qualquer batch futuro
- Padrão de secrets cache Windows formalizado (elimina rate limit recorrente)
- Adapter Hermes com handler `on_session_finalize` completo emitindo PR draft
- AGENTS.md §Adapter #4 protege trabalho futuro (auto-injetado)
- 8 issues do runtime contract Hermes shipadas em main
- 22 skills canônicas do framework projetadas no Hermes (`skill-bundles/`)

## Riscos residuais

1. **Rotação de secrets sem re-warm** — se rotaciona chave no 1P, cache local fica stale. Não temos auto-refresh (Fase 3 futura).
2. **CAIXA1 sem cache** — se algum agente rodar lá, ainda pode bater rate limit.
3. **PR de `own:hermes` misturado com trabalho manual** — se Felipe abre PR próprio na mesma janela, `/aprovar-pr` mistura.
4. **Rate limit 1P consumível pela SA** — cada rodada Hermes que rebuild cache consome N chamadas.

## Refs

- `stamper/skills/planejar-fila-hermes/SKILL.md` — skill principal
- `stamper/skills/planejar-fila-hermes/prompt-hermes.md` — prompt v8
- `stamper/skills/planejar-fila-hermes/lessons-learned.md` — 8 lessons
- `_core/HERMES-TRIGGER.md` — comando canônico Hermes
- `_core/SECRETS-PATTERN.md` — padrão adapter secrets
- `_core/DELL-NOTEBOOK-SETUP.md §6.2` — receita cache no Dell
- `_core/warm_secrets.py` + `_core/warm-op-env.ps1` — motor cache
- `_core/motor_select.py` — profile `hermes`
- `adapters/hermes/hook.py` — handlers wire protocol (start/pre_llm/pre_tool/post_tool/finalize)
- `_core/runtime/close_session.py` — close com trust_tier pr_only vs auto_main
- `AGENTS.md §Adapter #4 — Hermes` — regras duras auto-injetadas
- Linear document existente: [Doc: Warm secrets cache Windows + skill /planejar-fila-hermes (2026-08-14)](https://linear.app/cadencia/document/doc-warm-secrets-cache-windows-skill-planejar-fila-hermes-2026-08-14-e798ca08ca8f)
- Nota prévia do dia: `2026-08-14 Warm secrets cache — fix rate limit 1P + planejar-fila-hermes.md`
