---
date: 2026-05-25
tags: [ia, framework, agentes, arquitetura, constituicao, foundation, pd]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Constituição dos Times

> Doc fundador. Define o que um Time/Squad É, do que se compõe, como nasce, evolui e morre dentro do PD Framework.
> Fonte canônica: [pd-framework/_core/CONSTITUICAO-TIMES.md](https://github.com/felipeluissalgueiro/pd-framework/blob/main/_core/CONSTITUICAO-TIMES.md)

---

## Princípio fundador

Um **Time** = área da empresa. Um **Squad** = sub-área dentro de um Time. Squads aninhados quando sub-área tem ritmo próprio interno. **Profundidade reflete operação real, não burocracia.**

Toda criação é em sessão guiada com Felipe (regra absoluta). Sem ele, agente não cria.

---

## Anatomia de um Time (5 elementos canônicos)

```
times/<time>/
├── CLAUDE.md           ← manual do agente
├── memory/             ← estado vivo (STATE.md + decisions.md)
├── foundation/         ← docs constitutivos (compartilhados pelos Squads filhos)
├── context/            ← refs técnicas profundas (opcional)
├── skills/ + workers/  ← automações
└── <squad-a>/, <squad-b>/...
```

| Elemento | O que é | Muda quando |
|---|---|---|
| `CLAUDE.md` | Manual operacional agente | Raramente |
| `memory/` | Estado atual (STATE) + decisões | Toda sessão |
| `foundation/` | Docs constitutivos do Time | Raramente — pivot/rebrand |
| `context/` | Refs técnicas profundas | Mudança técnica |
| `skills/`+`workers/` | Automações | Conforme demanda |

**Não confundir `memory/`, `foundation/` e `context/`** — erro mais comum em monorepos multi-agente.

---

## Conceito-chave: `foundation/` (NOVO — decisão Felipe 2026-05-25)

Cada Time tem docs **constitutivos** que regem TUDO que os Squads filhos produzem. Baseados em frameworks consagrados.

### Sugestões por Time

| Time | Docs candidatos | Frameworks |
|---|---|---|
| **Marketing** | posicionamento, icp, anti-icp, narrativa, historia, tom-de-voz, brand, central-marca | Kotler, Osterwalder VPC, Aaker, Neumeier |
| **Comercial** | icp-comercial, playbook-objeções, rep-g, pipeline-structure | REP-G (PD), SPIN, MEDDIC |
| **CS** | icp-onboarding, processo-briefing, processo-crm-pd, sla-suporte | CRM-PD (PD) |
| **Produto** | SOUL.md cobre; pode add api-contracts, tech-principles | — |
| **Infra** | security-principles, runbook-overview, allowlist | SRE Google |
| **Financeiro** | dre-structure, regras-tributárias, ciclo-faturamento | Contabilidade gerencial |
| **Operacional** | cultura-pd, metas-trimestrais, processos-rh | OKRs |
| **Dev** | code-principles, padrão-testes, branch-convention | Clean Code, Conventional Commits |

**Popular conforme demanda** — não criar todos de cara.

### Enforço de consulta (3 níveis)

1. CLAUDE.md do Squad menciona foundation/ a consultar por tipo de asset
2. Skills do Squad carregam foundation no início do fluxo
3. Hook UserPromptSubmit futuro injeta paths por keywords

### Por que NÃO embedar/RAG

Claude Code lê MDs nativamente. RAG = over-engineering pra texto curto. MDs ficam editáveis, versionados em git, com diff visual, sem dependência de vector DB.

---

## Hierarquia variável (3, 4 ou 5 níveis)

- **3 níveis**: Time simples (`times/<time>/<squad>/`)
- **4 níveis**: Squad com sub-divisão (`times/<time>/<squad>/<sub-squad>/`)
- **5 níveis** (Cadência): produto complexo (`times/produto/cadencia/frontend/`)
- **Components/Features** (sem CLAUDE.md): estado vive no STATE do pai

**Regra simples:** tem `CLAUDE.md`? É Squad. Sem? É Component/Feature.

---

## Memória híbrida A+B+C

Time pai precisa saber estado dos Squads filhos. **Mesma função `aggregate_l1()`** em 3 mecanismos:

- **A — Manual**: `/fechar-squad` propaga L1 pro Time pai cascateado
- **B — On-demand**: `/abrir-squad <time>` calcula ao vivo
- **C — Cron noturno**: fallback automático 03h BRT (idempotente)

Felipe: _"funciono bem fechando manualmente mas às vezes esqueço, então podemos ter as 3 versões. Mas precisa ser determinístico."_

**STATE inicial = onboarding doc** populado (não placeholder).

---

## Integração Linear ↔ Squad

Toda issue/projeto tem UM Squad dono. Resolução em cascata:

1. Label `squad:<path>` (override)
2. `_core/linear-squad-map.json` por `project_id`
3. Sem dono → skill pergunta + oferece `/criar-squad`

**8 skills Linear integradas** registram automaticamente issues/projetos nos STATEs dos Squads. Sem isso, framework não reflete realidade.

---

## Como nasce um Time/Squad

Sempre `/criar-squad <area>` em **Modo Foco**:

1. Agente lê APENAS `CRIACAO-TIME-BRIEFING.md` (200 linhas) upfront
2. Busca refs sob demanda via `lookup.py`
3. Apresenta resumo pré-sessão
4. Pergunta lista numerada (9 perguntas — escopo, sub-squads, personas, workers, skills, pessoas, Linear, foundation, bloqueios)
5. Felipe responde numerado
6. Síntese + confirmação
7. Boilerplate (CLAUDE + memory + foundation se confirmado)
8. Atualiza linear-squad-map.json
9. Babysitting
10. Commit + push + reportar

**Tudo populado com decisões reais, não genérico vazio.**

---

## Times planejados (status)

| Time | Status |
|---|---|
| **Infra** | ✅ Criado (refator pendente — pré-regra "criar com Felipe") |
| **Marketing** | ⏳ Parcial mapeado (Conteúdo/Insight Artificial/Site PD/Brand) — sessão pendente |
| **Dev** | ⏳ 8 personas BR mapeadas — sessão pendente |
| **CS** | ⏳ Bot Telegram Suporte dentro — sessão pendente |
| **Produto/Cadência** | ⏳ 4 sub-squads mapeados — sessão pendente |
| **Comercial / Operacional / Financeiro** | ⏳ Sessão pendente |
| **Produto/{PD Portal, NSkin, GCI-GO, Consultorias, Cadência-Contato}** | ⏳ Sessão por produto |

---

## Como morre

Squad descontinuado vai pra `_archive/<nome>/`:
- Preserva histórico
- Remove do `linear-squad-map.json`
- Comentário no `decisions.md` do Time pai
- Issues Linear migram ou cancelam

Atuais em `_archive/`: azoto-academy, berro, hco, openclaw (uso comercial), karina, recovery-hertzner, etc.

---

## Notas relacionadas

- [[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]]
- [[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]]
- [[IA-Tecnologia/2026-05-24 PD Framework — SOUL.md vs CLAUDE.md vs STATE.md]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]

## Refs canônicas no repo

- `_core/CONSTITUICAO-TIMES.md` — fonte deste doc
- `_core/HIERARCHY.md` — detalhes níveis variáveis
- `_core/memory-schema.md` — STATE bracketed + A+B+C
- `_core/CRIACAO-TIME-BRIEFING.md` — Modo Foco criação
- `_core/SKILLS-LINEAR-INTEGRATION.md` — padrão Linear↔Squad
- `stamper/skills/criar-squad/SKILL.md` — skill de criação
