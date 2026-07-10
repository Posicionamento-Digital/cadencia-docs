---
date: 2026-06-24
tags: [doc, componente, lib, pdf, branded, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[marketing]]"]
---
# Doc Generator

## Identidade

- **Tipo:** lib Python + CLI (`_shared`)
- **Path:** `_shared/doc_generator.py` (334 LOC) · templates em `times/cs/foundation/templates-documentos/`
- **Render:** Chrome/Edge headless (`--print-to-pdf`) — sem dep PyPI
- **Status:** 🟢 produção (DEV-798)

## Templates

| Função | Template | Quem chama |
|---|---|---|
| `gerar_manual_cliente` | `manual-do-cliente.html` (Doc B) | consolidador Fase 1 |
| `gerar_guia_preparacao` | `guia-preparacao-call.html` (Doc A) | worker confirmacao-agenda véspera |
| `gerar_ata_reuniao` | `ata-reuniao.html` | pós-reunião |
| `gerar_dossier_cliente` | `dossier-cliente.html` | pós-briefing (interno) |
| `gerar_material_kickoff` | `material-kickoff.html` | antes kickoff |
| `gerar_deck_treinamento` | `deck-treinamento.html` | Fase 7 |

Helpers: `li_list`, `tr_rows`, `_esc`.

## Como funciona

1. `re.sub(r"\{\{\s*([\w.]+)\s*\}\}", ...)` substitui placeholders.
2. Escreve tmp HTML **na própria pasta de templates** (preserva `branding.css` + `assets/` relativos).
3. Chrome `--headless=new --no-pdf-header-footer --print-to-pdf=<out.pdf> file:///tmp`.
4. Deleta tmp.

## Branding

Cores: Azul Marinho `#0A1E3F`, Petróleo `#267788`, Bege `#D8CBB5`, Chumbo `#2C2C2C`, Dourado `#C9A84C`. Tipos: EB Garamond + Inter.

## Gotchas

- **F8 — ata data default:** `gerar_ata_reuniao(data="")` agora cai pra `date.today().isoformat()` (commit `7818eaf`). Antes gerava `Ata--.pdf` com slug vazio.
- Sem Chromium no Linux → `apt install chromium`.

## Don'ts

- Não usar `strict=True` em produção.
- Não escrever tmp fora da pasta de templates.

## Relacionadas

- [[04-Consolidador]] (gera Manual)
- Branded source: `pd-framework/times/marketing/foundation/brand.md`
