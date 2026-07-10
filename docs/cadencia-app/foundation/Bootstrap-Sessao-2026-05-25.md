---
date: 2026-05-25
tags: [sessao, cadencia, bootstrap, framework, playbook, log]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
linear: PDL-232, PDL-237, PDL-238, PDL-239, PDL-240, PDL-275
type: source
entities: ["[[Cadencia-Framework]]", "[[Cadencia]]", "[[PD Framework]]", "[[marketing]]"]
---
# Bootstrap Cadência no PD Framework — sessão 2026-05-25

> Sessão guiada Felipe + Stamper criando Squad pai PRODUTO Cadência no PD Framework (4 níveis hierárquicos). 5 issues Linear fechadas.

## Linear

| Issue | Status final | Descrição |
|---|---|---|
| PDL-232 | ✅ Done (Closes) | Squad pai Cadência |
| PDL-237 | ✅ Done (Closes) | Sub-squad frontend |
| PDL-238 | ✅ Done (Closes) | Sub-squad growth |
| PDL-239 | ✅ Done (Closes) | Sub-squad workers |
| PDL-240 | ✅ Done (Closes) | Blog (rebaixado pra feature — D03) |
| PDL-275 | 🆕 Backlog | Repopular skills /deletar-user + /visual-test |

## Decisões tomadas (D01, D02, D03)

1. **D01 — Bootstrap Squad Cadência completo**: Squad pai PRODUTO com SOUL.md + foundation + 3 sub-squads + 1 feature. Persona Catarina (PM/Owner — inspiração Marty Cagan + Teresa Torres). Distinta de Paloma (PO Dev transversal).

2. **D02 — Skills migram pro framework (A1)**: 4 skills do repo `cadencia-app/.claude/skills/` foram copiadas pra `times/produto/cadencia/skills/` com `CADENCIA_REPO` path absoluto. `/cadencia-debate` foi criada nova. Sandbox bloqueou deleção no repo Cadência — Felipe precisa rodar manual.

3. **D03 — Blog rebaixado de sub-squad para feature**: blog não tem ritmo/workers próprios — geração vive em `workers/`, deploy via Vercel template estático. Virou `features/blog/README.md`.

## Entregue na sessão

### Estrutura criada (`times/produto/cadencia/`)

- `SOUL.md` — Missão + Voz (declarativa, parcimoniosa, Maga/Sábia) + 6 Valores + Identidade visual (paleta `#4F46E5` índigo + `#10B981` esmeralda + Inter) + 8 Princípios técnicos
- `CLAUDE.md` — manual Squad pai com persona Catarina
- `memory/STATE.md` (L1/L2/L3 onboarding agregado dos 3 sub-squads)
- `memory/decisions.md` (D01, D02, D03)
- `foundation/` — 5 docs constitutivos + README
- `context/roadmap-snapshot.md` — snapshot 25/05 dos 2 projetos Linear
- `features/blog/README.md` — white-label template `cadencia-blog-template`
- 3 sub-squads (frontend/growth/workers) cada um com CLAUDE+STATE+decisions
- 5 skills locais

### Framework atualizado

- `_core/PERSONAS.md` — Catarina adicionada (inspiração Marty Cagan + Teresa Torres)
- `_core/state-aggregator.py` — fix: `workers/` com CLAUDE.md vira sub-squad legítimo
- `_core/linear-squad-map.json` — 3 projetos Cadência já mapeados (validado)

### Commits

- `5825887` — bootstrap completo (5 Closes)
- `aaf15c9` — fix aggregator workers/

### Linear

- 5 PDLs movidas Backlog → Done via Closes
- PDL-240 com comentário explicando rebaixamento (D03)
- PDL-275 criada (Backlog P3) — repopular `/deletar-user` + `/visual-test`

## Surpresas durante a sessão

1. **n8n stack `cadencia-n8n-*` na VPS Master** não tem haver com produto Cadência — só compartilha nome (Felipe esclareceu)
2. **`assessoria-imprensa-cadencia`** vive em Marketing/Comunicação, não no Squad Cadência
3. **Blog rebaixado** pra feature ao invés de sub-squad (D03)
4. **Catarina** ao invés de Luana (Felipe vetou Luana)
5. **Skills `/deletar-user` + `/visual-test`** vazias no repo Cadência — viram backlog PDL-275
6. **Bug no `state-aggregator.py`** — pulava `workers/` por convenção hardcoded de nome. Fixado pra detectar via presença de CLAUDE.md.

## Pendências pós-sessão

1. **Deletar skills do repo Cadência** (sandbox bloqueou):
   ```bash
   cd "Projetos BMAD/Cadencia/.claude/skills"
   rm -rf cadencia-review-deploy capi-test gerenciar-plano analytics-report
   ```
2. **PDL-275** — repopular `/deletar-user` + `/visual-test`
3. **TODO técnico** — adaptar `analytics_notion.py` → `analytics_obsidian.py`

## Como abrir o Squad

```
/abrir-squad times/produto/cadencia
/cadencia-debate
/catarina
```

## Notas relacionadas

- [[Cadencia-Framework/Docs/README]]
- [[MOC-Projetos]]
