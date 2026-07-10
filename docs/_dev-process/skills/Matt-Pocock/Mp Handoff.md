---
date: 2026-05-14
tags: [skill, matt, pocock, handoff, contexto, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Mp Handoff

Compacta a conversa atual em documento de handoff para outro agente pegar.

## Quando usar
"compacta isso pra outro agente", "handoff". Para passar contexto entre sessões Claude.

---

## Conteúdo da Skill

```markdown
---
name: mp-handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to a path produced by `mktemp -t handoff-XXXXXX.md` (read the file before you write to it).

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
```

## Notas Relacionadas
[[Stamper-Operacionais/Handoff Sessao]] · [[Stamper-Operacionais/Resumo Pra Colar]]
