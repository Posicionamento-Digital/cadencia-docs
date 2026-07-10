---
date: 2026-06-27
tags: [doc, componente, cadencia-growth]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
# cadencia-growth → crons/

Entry points cron — invocados pelo crontab root da VPS Master.

## Identidade
- **Tipo:** scripts batch
- **Stack:** Python 3.12 · flock
- **Path:** `crons/`
- **Status:** ativo

## Arquivos e schedules
- `growth_pipeline.py` — `0 14 * * *` (sync blog linkedin instagram) + `0 18 * * 5` (newsletter)
- `retry_provisioning.py` — `55 13 * * *`
- `cleanup_orphan_ideas.py` — `*/5 * * * *`

## Não vive aqui
`cadence_tick.py` (motor cadências) está em `pipeline/cadence_tick.py`, cron `10 14 * * *` direto.

## Don'ts
- Não rodar `growth_pipeline.py` manual sem flock — pode colidir com cron
- Não mudar schedule sem atualizar docs/

## Notas Relacionadas
[[Projetos/Cadencia-Growth/Docs/README]] · [[Projetos/Cadencia-Growth/Docs/pipeline]]