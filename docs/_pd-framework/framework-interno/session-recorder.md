---
date: 2026-07-03
tags: [doc, componente, pd-framework, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]"]
---

# Session Recorder — black box de sessões (D3)

## Identidade
- **Tipo:** lib/CLI determinística + backend do lookup (core)
- **Stack:** Python 3.12 + SQLite, zero deps
- **Path:** `_core/session_recorder.py` · `_lookup_backends/transcripts.py` · `_core/clean_transcripts.py`
- **Issues:** epic DEV-1117 (stories DEV-1118…1121)
- **Status:** ativo

## O que é
A camada de RESGATE da D3: sessão que morre sem `/encerrar-sessao` deixava de existir pro sistema de memória. Agora todo turno (pedido + resposta + tools + arquivos tocados) é capturado do transcript do harness com **resumo extrativo sem LLM**, deduplica por fingerprint e fica consultável. Memória curada (sessions-log/STATE/decisions) continua sendo a fonte nobre.

## Como funciona
1. **Captura:** parser do JSONL em turnos (tool_results/system-reminders não abrem turno; synthetic ignorado).
2. **Store:** SQLite WAL `.pd/recorder/turns.db` (PK=fingerprint → idempotente) + fallback JSON. Primeiro run real arquivou **1.286 turnos do histórico completo**.
3. **Resgate:** `lookup --source transcripts` (**opt-in por design** — turno cru não polui busca default nem índice D1).
4. **Limpeza integrada:** `clean_transcripts.py --apply` arquiva o pd-framework no recorder ANTES de deletar (não-pulável).

## Quickstart
```bash
python _core/session_recorder.py capture --all-sessions
python _core/session_recorder.py tail --limit 10
python _core/lookup.py "o que eu estava fazendo" --source transcripts
python _core/clean_transcripts.py --days 30          # preview; --apply só com confirmação
```

## Don'ts
- Nunca tratar o recorder como memória nobre — é resgate.
- Nunca deletar transcripts do pd-framework sem passar pelo `clean_transcripts.py`.
- Nunca ativar `transcripts` no ACTIVE do lookup (decisão registrada — flood).

## Troubleshooting
- **0 turnos no preview** → rodar do diretório do repo (o default resolve o projeto pelo cwd).
- **Resgate de outra máquina** → store é local por máquina, por design.
- **Skill /limpar-transcripts global ainda com fluxo antigo** → pendência de permissão registrada na DEV-1121; usar o script no framework.

## Histórico
- 2026-07-03 — epic completo: 8afb2cf (captura) · 879865e (store, 1.286 turnos retroativos) · 45be2e7 (source lookup) · b6af5e8 (limpeza integrada) · d8b46e9 (docs)

## Notas Relacionadas
[[memory-engine]] · [[outcomes-cost]] · repo: `_core/docs/session-recorder.md` · manual §10.5
