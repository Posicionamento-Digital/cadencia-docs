---
type: source
source_kind: decisao
date: 
entities: ["[[comercial]]", "[[produto]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Decisões — produto-treinamentos-memory

# Decisões — Squad Treinamentos

(append-only — decisões relevantes ficam aqui, mais recente em cima)

---

## 2026-07-02 — Squad Treinamentos criado, persona Renata

**Contexto:** Treinamentos vivia disperso — pastas de aluno soltas e duplicadas direto em `times/produto/treinamentos/<aluno>/`, sem persona nem STATE próprios, sem lugar único pra gotchas de condução de aula.

**Decisão:** criar squad próprio (`times/produto/treinamentos/CLAUDE.md`, persona **Renata** — PM/Owner do programa, não substitui Felipe como instrutor). Programa comercial batizado **"Programar com IA"**, cobrindo as duas modalidades (Imersão 1 dia + Treinamento 30d) sob uma pasta-mãe única (`programar-com-ia/`).

**Impacto:** todo aluno novo entra em `programar-com-ia/<slug>/`. Gotchas de condução de aula (triagem de nível, escopo x tempo, mentalidade) centralizados em `programar-com-ia/gotchas-treinamentos.md`, consulta obrigatória antes de qualquer sessão nova.

**Quem decidiu:** Felipe.

---

## 2026-07-02 — Eliseu Rocha removido dos registros (negociação não fechou)

**Contexto:** Eliseu Rocha aparecia em múltiplos registros do produto (STATE, tabela de vendas) como aluno fechado em 08/06/2026, com status "desconhecido" pendente de confirmação.

**Decisão:** Felipe confirmou que a negociação não fechou de fato — Eliseu não é aluno. Removido de todas as tabelas/registros ativos do squad e do produto.

**Quem decidiu:** Felipe.
