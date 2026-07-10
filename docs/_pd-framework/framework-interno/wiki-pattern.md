---
type: source
source_kind: doc
date: 2026-06-29
entities: ["[[PD Framework]]"]
tags: [doc, wiki, framework]
moc: "[[MOC-Projetos]]"
---

# LLM Wiki Pattern — Playbook

> Sistema que torna os vaults Obsidian wikis vivas auto-mantidas (modelo Karpathy). DEV-955 (Empresa) + DEV-974 (Pessoal).

## O que é
3 camadas: **raw** (pd-framework / conteúdo nativo) → **wiki** (vault) → **schema** (`Setup/AGENTS.md`). Entities (cliente/projeto/autor/conceito) são hubs; sources (sessões/leituras) apontam via `entities:` no frontmatter. Bookkeeping por cron, não por skill.

## Componentes (em `pd-framework/_shared/`)
- **obsidian_client.py** — helpers `mirror`/`ensure_entity`
- **wiki_backfill.py** — backfill Empresa (catálogo+matcher+sanitização) → 27 entities + 293 sources
- **wiki_connect.py** — consolidação in-place Pessoal → 21 hubs + 30 sources
- **wiki_maintain.py** — ingest+lint no cron `WikiMaintain-Daily` (18:15)

## Operação
- Cron diário liga notas novas + roda lint (`Setup/_wiki-lint.md`)
- Reversão: git baseline por vault (Empresa `7f44556`, Pessoal `89348a8`)

## Don'ts
- Não espelhar STATE/MEMORY vivos, código, segredos
- Não tocar arquivos-fonte do pd-framework pelo vault
- Doc técnica completa: `pd-framework/_shared/WIKI-PATTERN.md`
