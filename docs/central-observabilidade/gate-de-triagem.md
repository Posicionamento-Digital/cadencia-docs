---
date: 2026-07-06
tags: [doc, documentacao, projeto, observabilidade]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]"]
---
# Gate de triagem — classificação + roteamento de ownership

## TL;DR
Segundo papel da bridge (`POST /linear-webhook`, repo `Posicionamento-Digital/health-check` → `bridge/app/classify.py` + `main.py`). Quando a bridge cria uma issue do Sentry (`own:triagem`), o gate classifica o erro e roteia o dono — determinístico, sem LLM (a Master é determinística).

## Classificação (precedência ruído > infra > bug)
| Categoria | Destino | Critério |
|---|---|---|
| `ruído` | Canceled | browser/service-worker (appendChild, ResizeObserver, scriptURL, ChunkLoad) |
| `infra` | `own:felipe` | 429, ECONNREFUSED, 502/503, upstream (dependência externa) |
| `bug` | `own:agente` | culprit = path de arquivo OU rota HTTP (`/api/...`) — o que o autofix do cadencia-app tenta |
| `incerto` | **`own:felipe`** | sem regra clara (culprit vazio/`?`) → revisão humana. **NUNCA órfão em `own:triagem`** |

## Regra de design (DEV-1188)
`bug` (→ autofix) exige culprit de código NOSSO. Erro **sem culprit** (worker capturado por log, dado faltando) NÃO vira bug: cai em `incerto` → `own:felipe`. O gate **não adivinha bug pelo título** de propósito — confundiria dado-faltando de worker com bug de código, mandando trabalho inútil pro autofix (que só cobre cadencia-app). A garantia contra órfã vive no roteamento (`incerto→felipe`).

## Anti-loop
`run_gate` só age em issue com `own:triagem` (lock). `apply_ownership` remove qualquer `own:*` e aplica o novo — então mover pra felipe/agente tira do escopo, sem re-disparo.

## Histórico
- 2026-07-05/06 (DEV-1188) — `incerto` deixava bug de worker órfão em `own:triagem` por 1 dia. Fix: `incerto → own:felipe`. E2E validado: issue sem culprit vira own:felipe em ~2s. PR #7.
- 2026-06-29 (DEV-952) — culprit-como-rota HTTP não era reconhecido como bug. Corrigido.

## Fluxo completo do loop
bridge cria issue (own:triagem) → **gate classifica/roteia** → `own:agente` (autofix cadencia-app, cron Dev /15min) OU `own:felipe`/`own:luiz` (humano) OU Canceled (ruído).

## Notas Relacionadas
[[suporte-botao-ajuda]] · [[Incidentes/2026-07-05_gate-classifica-so-por-culprit-issues-orfas]]
