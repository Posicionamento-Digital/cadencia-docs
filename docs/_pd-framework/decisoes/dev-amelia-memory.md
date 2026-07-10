---
type: source
source_kind: decisao
date: 
entities: ["[[dev]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---

# Decisões — dev-amelia-memory

# Decisões — Squad Amélia

(append-only — decisões operacionais de babysitting/execução, mais recente em cima)

---

## 2026-05-25 — Squad criado (PDL-256)

Squad Amélia criado como parte do bootstrap do Time Dev. Sem decisões operacionais ainda.


---

## 2026-06-05 — `/encerrar-sessao` como porta única de saída + hook checkout-warning (PDL-422)

**Problema:** hooks session-branch desenhados pra fluxo único `main → session/* → main` em checkout único. Felipe usa worktrees paralelos + sessões multi-PDL + branches `feat/pdl-X` frequentes. Trabalho órfão (24 modif + 25 untrack travados em feat/pdl-382 ao diagnosticar).

**Decisão Vitor:** `/encerrar-sessao` vira porta única de saída controlada. Hook automático mantém-se como fallback (sem regressão). Lógica por tipo de branch (5 casos). Default em `feat/pdl-X` = salvar sem fechar PDL (Felipe nem sempre fecha PDL em 1 sessão).

**Rejeitadas:**
- Stop automático em qualquer branch ≠ main: quebra atomicidade Linear↔git (`/linear-close-issue` é dono).
- Só documentação: depende de disciplina humana (Felipe TDAH, Luiz pode esquecer).

**Hook novo:** `pretooluse-checkout-warning.py` — tripwire pra evitar mudar de branch dirty (causa raiz da contaminação cross-branch).

**Reviews:** `/codex-review` + `/runtime-fix-review` (não é auth/billing/migration, mas hook em git event-Stop = risco regressão alto).

**Impacto Luiz:** zero mudança visível. Workflow `feat/pdl-X` preservado.
