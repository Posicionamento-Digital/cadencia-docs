---
date: 2026-06-27
tags: [doc, componente, cadencia-growth]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
# cadencia-growth → scripts/

Scripts operacionais — migrações, validação, recovery manual. Não cron.

## Identidade
- **Tipo:** scripts one-shot
- **Stack:** Python 3.12 + bash
- **Path:** `scripts/`
- **Status:** ativo

## Arquivos chave
- `drift_check.sh` — valida sync `/cadencia` ↔ repo (irrelevante pós-migração Coolify)
- `migrate_ghl_*.py` — migrações one-shot GHL → Resend
- `recover_orphan_provisioning.py` — recovery manual de tenant em orphan
- `email_resend_preflight.py` — pre-check cutover Resend
- `content_readiness.py` — auditoria tenants
- `test.sh` — wrapper pytest

## Don'ts
- Não rodar `migrate_*` 2x no mesmo tenant (borderline duplica)
- Não ignorar alerta `drift_check.sh` — captura diff e versiona ANTES de `git pull`

## Notas Relacionadas
[[Projetos/Cadencia-Growth/Docs/README]] · [[Projetos/Cadencia-Growth/Docs/crons]]