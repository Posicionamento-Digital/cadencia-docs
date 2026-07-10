---
date: 2026-06-27
tags: [doc, componente, cadencia-growth]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
# cadencia-growth → mission_control.py

Dashboard HTTP de operação. Mostra crontab + ps + tails de log da VPS.

## Identidade
- **Tipo:** daemon HTTP
- **Stack:** Python 3.12 · http.server stdlib
- **Path:** `mission_control.py` (raiz do repo)
- **Porta:** `:8768` (http://72.60.4.71:8768)
- **Status:** ativo
- **Auth:** opcional via `DASHBOARD_SECRET` (sem ele = público)

## O que mostra
- Crontab atual (filtrado por projeto)
- ps aux dos processos persistentes esperados
- Tails de log (growth_pipeline.log, trigger.log, scoring.log)
- Auto-refresh 30s
- Mobile-first

## Don'ts
- Não expor publicamente sem `DASHBOARD_SECRET` em prod aberta — vaza estrutura do sistema

## Notas Relacionadas
[[Projetos/Cadencia-Growth/Docs/README]]