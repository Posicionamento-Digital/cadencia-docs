---
date: 2026-05-14
tags: [ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# start-issue

Skill para iniciar trabalho em uma issue do Linear.

Consultar: `C:\Users\felip\.claude\skills\start-issue\SKILL.md`

---

**Uso:** `/start-issue` (lista) ou `/start-issue PDL-11` (direto)

**O que faz:**
1. Lista issues atribuídas ao usuário no ciclo atual
2. Faz checkout da branch correspondente no repo certo
3. Marca a issue como In Progress no Linear

**Dependência:** `LINEAR_API_TOKEN` em `/root/.claude/.env` ou env var

## Notas Relacionadas
[[Skill]] - [[Skills]]
