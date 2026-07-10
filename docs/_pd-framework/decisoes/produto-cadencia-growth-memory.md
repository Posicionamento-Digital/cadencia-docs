---
type: source
source_kind: decisao
date: 
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]", "[[PD Framework]]", "[[produto]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Decisões — produto-cadencia-growth-memory

# Decisões — Sub-squad growth Cadência

(append-only — mais recente em cima)

---

## 2026-05-25 — Bootstrap sub-squad growth (PDL-238)

**Contexto:** Sub-squad aninhado criado durante bootstrap Squad pai Cadência (PDL-232). Pipeline já operava na VPS Hostinger `/cadencia/` — só faltava formalizar como sub-squad do PD Framework.

**Decisão:** Pasta `growth/` com CLAUDE.md + memory/STATE.md + decisions.md. Sem skills/workers próprios (compartilha skills com Squad pai). Cobertura: 3 crons (blog+seinfeld, LinkedIn, newsletter) + webhook scoring systemd + pipeline Python.

**Impacto:** Growth tem identidade própria no framework, ligada ao projeto Linear `3d140e11` (Separação Repo + Migração VPS). Migração `/cadencia/` → `/opt/cadencia-growth/` + Coolify continua via PDL-213, 215.

**Quem decidiu:** Felipe
