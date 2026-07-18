---
date: 2026-06-29
tags: [documentacao, infra, observabilidade, cadencia]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]"]
---
# Central de Observabilidade + Auto-correção com IA

> Loop que transforma erro de produção em PR de correção **sem humano no meio** — até o gate de aprovação. Projeto Linear: **Central de Observabilidade + Auto-correção com IA** (`91d67a96`).

## O que é

Um pipeline de 3 estágios que detecta um erro em produção (Sentry), abre uma issue no Linear, **classifica** o erro, e — se for bug acionável no nosso código — dispara um **agente Claude autônomo** que diagnostica, corrige, testa e abre um PR. O humano só entra no fim, para aprovar o merge.

```
Sentry  ──►  bridge (cria issue own:triagem)  ──►  gate (classifica)
                                                      │
                          ruído→Canceled · infra→own:felipe · incerto→fica
                                                      │ bug
                                                      ▼
            own:agente  ──►  worker (poll/claim)  ──►  agente Claude headless
                                                              │ cascata Linear
                                                              ▼
                                          PR aberto + own:review  ──►  Felipe aprova (/aprovar-pr)  ──►  deploy
```

## Os 3 estágios (componentes)

### 1 + 2. `sentry-linear-bridge` — bridge + gate

- **Repo:** `felipeluissalgueiro/sentry-linear-bridge` · **Deploy:** Coolify VPS Master (app `cadencia/sentry-linear-bridge`), `https://sentry-bridge.cadencia.app.br`, auto-deploy on-commit no `main`.
- **`POST /`** (bridge): recebe webhook do Sentry (valida HMAC), cria issue Linear em `own:triagem` + `tipo:bug` no projeto *maint: Cadencia — Bugs e suporte*. Dedup por marcador `[sentry:<id>]` no título.
- **`POST /linear-webhook`** (gate, CAD-687): escuta o webhook do Linear (issue create/update). **Só age em `own:triagem`** (lock anti-loop). Chama `classify.py` e aplica o ownership.
- **`classify.py`** — heurística **determinística, sem LLM** (a Master é determinística, SECURITY.md §1). Precedência **ruído > infra > bug**:
  - `ruído` → Canceled (markers de browser/service-worker: appendChild, ResizeObserver, AbortError, ChunkLoadError, **scriptURL**, etc.)
  - `infra` → `own:felipe` (rate limit / conexão: 429, ECONNREFUSED, 502/503, upstream)
  - `bug` → `own:agente` (culprit = **path de arquivo** `.ts/.py/src/app/...` **OU rota HTTP** `/api/...`, `GET /x` — âncora `(?:^|\s)/` pra não casar URL de terceiro)
  - `incerto` → fica em `own:triagem` (revisão humana)
- Notifica o Felipe no WhatsApp (Stevo) por categoria — **nunca** ruído.

### 3. `cadencia-autofix` — worker de auto-correção (CAD-689)

- **Repo:** `felipeluissalgueiro/cadencia-autofix` · **Roda:** VPS Dev (`~/cadencia-autofix`), cron `*/15min` sob `flock` (1 instância). Deploy = `git pull` na Dev.
- **Por que na Dev e não na Master:** a Master é proibida de rodar agente com tool use (SECURITY.md §1). O agente Claude headless roda na Dev.
- **Fluxo:** `poll_agent_issues()` (own:agente em Triage) → `claim()` (→ In Progress) → `run_agent()` dispara `claude -p` headless no `~/cadencia-app` com **allowlist** de tools (default-deny).
- **Sinal de sucesso:** `has_open_pr()` — PR aberto cuja branch referencia o identifier (regex de **fronteira ancorada** `(^|[^a-z0-9])ident([^0-9]|$)` pra não confundir `dev-94`/`dev-944`). Sucesso → `own:review`. Falha/cap → `own:luiz` + dossiê + WhatsApp pro dev externo (CAD-690).
- **O worker controla os labels `own:*`, não o agente** (fonte única de verdade).

## A cascata do agente (prompt do worker, DEV-953)

O `build_prompt()` instrui o agente Claude a conduzir a **cascata Linear oficial**:

1. **Knowledge Lookup** (`lookup.py`) — esse bug já apareceu antes?
2. **/debug-polya** — **OBRIGATÓRIO** (sem humano no loop, o diagnóstico de causa raiz é a salvaguarda contra fix superficial)
3. **/linear-planejar-issue** — plano técnico + cria branch (modo não-interativo: defaults, sem perguntar — está headless)
4. **/linear-start-issue** — checkout + In Progress
5. **Corrige** (personas Amélia → Camila) + **prevenção** (teste anti-recorrência)
6. build + lint + testes
7. **/linear-e2e-test --runs 1** — valida ponta-a-ponta; **proibido efeito irreversível em produção** (deleção/cobrança/envio real/deploy) — pula e anota pro humano se preciso
8. **/openrouter-review**
9. **Abre PR e PARA** (own:review) — corpo do PR num template obrigatório
10. **/registrar-incidente** se causa não-óbvia · **/encerrar-sessao** no `times/dev`

## Contrato de ownership (CAD-686)

Label group exclusivo `ownership` (lock nativo do Linear). Estados e IDs:

| Label | ID | Significado |
|---|---|---|
| `own:triagem` | `24dd7897` | estado inicial (bridge nasce aqui) |
| `own:agente` | `52849777` | bug acionável → worker pega |
| `own:felipe` | `46c220e0` | infra/externo (alçada do Felipe) |
| `own:luiz` | `d6feb9a8` | agente não resolveu → escalado |
| `own:review` | `4dddb313` | PR aberto, aguarda aprovação |

## Regras absolutas (gotchas)

- 🚫 **VPS Master nunca roda agente com tool use** — só o gate determinístico. Agente Claude só na VPS Dev. (SECURITY.md §1)
- 🚫 **O agente NUNCA mergeia nem roda `/linear-close-issue`** — close faz merge+deploy, decisão humana. Felipe aprova via `/aprovar-pr`. (DEV-WORKFLOW §12.0b)
- 🚫 **O agente não mexe nos labels `own:*`** — quem controla é o worker.
- ⚠️ **Deploys:** bridge = auto-deploy Coolify on-commit; worker `cadencia-autofix` = `git pull` na Dev; o `cadencia-app`/`cadencia-workers` = auto-deploy Coolify on-commit no master (o fix do agente só fica ativo após esse redeploy).

## 🔥 Troubleshooting — "a central criou a issue mas não corrigiu"

Sintoma real (2026-06-29): issues `[sentry:...]` paradas em **own:triagem / Triage**, sem PR. Diagnóstico:

1. **A issue está em `own:agente`?** Se está em `own:triagem`, o **gate** não promoveu. Cheque o `classify()` no container da bridge:
   `docker exec <bridge> python -c "from app.classify import classify; print(classify('<title>','<culprit>','error'))"`
   — se devolve `incerto` pra um bug óbvio, é falha de classificação (foi a causa-raiz da DEV-952: culprit como rota HTTP não casava `CODE_HINTS`).
2. **O worker está vivo?** `run.log` na Dev mostra `own:agente em Triage: N` a cada 15min. Se `N=0` sempre e há bug real em `own:agente`, ver poll/credencial.
3. **Worker pega mas escala pro dev externo sempre?** Cheque `has_open_pr` — se a branch do agente não casa o identifier, o sucesso não é detectado.

## Histórico

- **2026-06-29** — Diagnóstico + ressuscitação do loop (estava morto desde sempre, nunca tinha rodado e2e):
  - **DEV-952** (gate): `classify.py` só marcava `bug` quando culprit era path de arquivo; o Sentry manda **rota HTTP** → tudo caía em `incerto` e travava. Fix: regra de culprit-como-rota (regex ancorada) + `scriptURL` no ruído. Testes 17/17.
  - **DEV-953** (worker): `build_prompt()` reescrito pra a **cascata Linear oficial** (`/debug-polya` obrigatório); `has_open_pr` ancorado em fronteira.
  - **DEV-944** (voo e2e): primeiro ciclo ponta-a-ponta real. Gate promoveu → worker → agente diagnosticou (`finish_reason=error` era retryable, não exceção imediata) e corrigiu `cadencia-workers/src/shared/llm.py` → PR #80 → revisado (2 P2 aplicados) → merge owner → Coolify auto-deploy. **Loop fechado.**

## Notas relacionadas

[[MOC-Infra]] · `_core/SECURITY.md` · `_core/DEV-WORKFLOW.md` §12.0b · `_core/RUNTIME-CONTRACT.md`
