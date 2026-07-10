---
date: 2026-07-03
tags: [doc, componente, pd-framework, skill, documentacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[PD Framework]]", "[[qualidade]]"]
---
# Skills Tooling — qualidade de skill como código (D4+D6)

## Identidade
- **Tipo:** lib/CLI + hook (core)
- **Stack:** Python 3.12, zero deps
- **Path:** `_core/lint_skills.py` · `_core/hooks/stop-skills-lint.py` · `_core/new_skill.py`
- **Issues:** epic DEV-1122 (stories DEV-1123…1126)
- **Status:** ativo

## O que é
Tooling que elimina a classe "skill quebrada silenciosamente": linter em lote, guarda de regressão no fechamento e scaffolder que torna impossível criar skill inválida. **Estreia do linter: 25 skills quebradas em 199** — a classe do Adapter Codex (5 conhecidas) era 5× maior.

## Como funciona
1. **Linter:** erros estruturais (frontmatter/BOM/limites) vs warnings de qualidade (gatilho de ativação; critério ADR-112 "quando NÃO usar/alternativa" — 170 no legado). Modo relatório por design.
2. **Guarda no Stop:** baseline monotone-decreasing — silencioso no legado, avisa só quando quebradas SOBEM, baseline desce quando consertam. Nunca bloqueia.
3. **Scaffolder:** `new_skill.py` gera skill nos 2 formatos do `/abrir-squad`, description ADR-112-completa, gate de lint (reprova → arquivo removido), registro no INVENTORY.
4. **D6:** template CAD-Bug com `## Impacto` + `## Evidência` no arquivo canônico.

## Quickstart
```bash
python _core/lint_skills.py --verbose
python _core/new_skill.py --name x --squad times/dev --what "..." --triggers '"/x"' --not-for "para Y — use /outra"
```

## Don'ts
- Nunca criar skill na mão sem passar pelo scaffolder ou pelo linter depois.
- Nunca commitar `.pd/skills-lint-baseline.json` (derivado local).

## Troubleshooting
- **Aviso "SKILLS QUEBRADAS SUBIRAM" no fechamento** → `python _core/lint_skills.py` mostra quais; consertar ou reverter a skill nova.
- **Scaffold reprovou no lint** → bug de input (description curta demais/sem componentes) — o erro mostra o motivo.

## Pendências (Felipe, ~5 min)
- Criar o arquivo da skill `/criar-skill` (guia que chama o `new_skill.py`) — dirs de skills protegidas na sessão de implementação.
- Replicar Impacto+Evidência no template Bug da UI do Linear.
- Decidir se conserta as 25 skills quebradas legadas (issue própria por squad).

## Histórico
- 2026-07-03 — epic completo: 43303aa (linter, 25 achadas) · 36890d3 (guarda Stop) · 1879cca (scaffolder) · 5b26a71 (template D6) · dec108a (docs)

## Notas Relacionadas
[[memory-engine]] · [[model-map]] · [[session-recorder]] · repo: `_core/docs/skills-tooling.md` · manual §10.6
