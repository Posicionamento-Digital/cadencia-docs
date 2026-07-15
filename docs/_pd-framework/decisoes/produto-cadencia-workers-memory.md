---
type: source
source_kind: decisao
date: 
entities: ["[[Cadencia]]", "[[produto]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Decisões — produto-cadencia-workers-memory

# Decisões — Sub-squad workers Cadência

(append-only — mais recente em cima)

---

## 2026-05-25 — Migração Railway → Coolify VPS Master é decisão arquitetural

**Contexto:** Cadeia PDL-18 a 23 trata da migração dos workers Coolify VPS Master → Docker Compose VPS Master (Coolify). Race condition histórica entre Railway worker pool e VPS pool gerou incidents (25/04 generation_queue, 15/05 ideias presas).

**Decisão:** Workers vão migrar de Railway pra Coolify VPS Master. Path no servidor: `/opt/cadencia-workers/` (paralelo a `/opt/cadencia-app/` já presente). Após migração, push `master` vai pro Coolify. Pós-migração, validar ausência race condition (PDL-21) + cancelar serviços Railway.

**Alternativas consideradas:**
- Manter Railway (custo crescente + race conditions documentados — rejeitado)
- Railway + Coolify paralelo permanente (overhead operacional — rejeitado)

**Impacto:**
- `railway.toml` vira docker-compose Coolify
- Healthcheck `/health` continua válido (Coolify suporta)
- Env vars: PDL-215 In Progress (6 apps)
- Cron-job.org → cron Coolify nativo

**Quem decidiu:** Felipe (decisão herdada do projeto Linear `3d140e11`)

---

## 2026-05-25 — Bootstrap sub-squad workers (PDL-239)

**Contexto:** Sub-squad aninhado criado durante bootstrap Squad pai Cadência (PDL-232).

**Decisão:** Pasta `workers/` com CLAUDE.md + memory/STATE.md + decisions.md. Sem skills próprios (compartilha com Squad pai). Cobertura: pipeline 7-step + agents + renderer + integrations + tests.

**Impacto:** Workers tem identidade própria. Decisões sobre LLM stack, renderer, pipeline ficam aqui. Decisões cross-stack vão pro Squad pai.

**Quem decidiu:** Felipe
