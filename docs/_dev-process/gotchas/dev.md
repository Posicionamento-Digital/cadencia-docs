---
type: source
source_kind: gotcha
date: 
entities: ["[[Cadencia]]", "[[dev]]"]
tags: [gotcha, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Gotchas — dev

# Gotchas — times/dev

> Armadilhas técnicas validadas (manual review).
> Source: entries promovidas de gotchas-pending.md (auto-detect).

## Path POSIX (`/c/dev/...`) vs Path Windows (`C:\dev\...`) em subprocess/python direto

**Categoria:** Ambiente Windows · **Impacto:** médio — quebra silenciosamente ou dá `FileNotFoundError`/`[WinError 267]`, confunde diagnóstico.

**Origem:** DEV-909 (2026-06-27, `_core/runtime/close_session.py`). **Confirmado de novo em 2026-07-01** (sessão retrofit Mel Quevedo) — ao rodar `python -c "..."` logo após `cd` pra um repo externo (`cadencia-cli`), scripts que abriam arquivo com path relativo (`open('times/cs/skills/.../SKILL.md')`) davam `FileNotFoundError` porque o cwd real do shell (Windows) não batia com o path POSIX assumido no bash tool.

**Padrão de fix:**
```python
try:
    cwd = str(Path(cwd_raw).resolve())
except Exception:
    cwd = cwd_raw
```
Ou, na prática do dia a dia: sempre confirmar `pwd`/cwd real antes de abrir arquivo com path relativo após qualquer `cd`, especialmente logo após sair de um repo externo.

**Onde validado:** `_core/runtime/close_session.py` (DEV-909) + confirmado empiricamente em scripts ad-hoc na sessão de 2026-07-01.

**Propagar pra:** revisar todos os scripts em `_core/runtime/*.py` + `_core/*.py` que recebem path externo via stdin JSON ou CLI args. Ainda vale auditoria (não feita nesta sessão).

---

## Linear auto-move issues por commit com `Refs DEV-X` (integração GitHub)

**Sintoma:** issue muda de estado sozinha (ex.: Todo → In Review) sem ninguém tocar no Linear.

**Causa:** a integração GitHub do Linear anexa commits cuja mensagem referencia a issue (`Refs DEV-1141`, magic words em geral) e dispara transição automática de estado. Descoberto em 2026-07-03 quando DEV-1141 apareceu "In Review" após um commit na main com `Refs DEV-1141` — inicialmente confundido com bug do `linear_claims.py` (que também existia, mas era outro: `_state_id` pegava In Review por ser o primeiro estado type=started).

**Regra prática:** (1) usar `Refs` só quando a transição automática for desejada — pra citar sem mover, mencionar o ID fora do padrão magic word ou só no corpo do comentário Linear; (2) ao debugar estado inesperado de issue, checar os attachments dela (commits anexados) antes de suspeitar do código; (3) o motor 24/7 pode USAR isso a favor (transição de graça no push), mas precisa prever que estados mudam por fora.

**Onde validado:** DEV-1141, attachments do commit `5f20884` (2026-07-03).
