---
date: 2026-05-25
tags: [ia, framework, agentes, arquitetura, memoria, pd]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Hierarquia Time/Squad e memory híbrida

> Decisões estruturais 25/05/2026. Atualiza notas anteriores:
> - [[IA-Tecnologia/2026-05-23 PD Framework — arquitetura de squads e Stamper como orchestrator]]
> - [[IA-Tecnologia/2026-05-24 PD Framework — Arquitetura completa e mapeamento de stack]]
> - [[IA-Tecnologia/2026-05-24 PD Framework — SOUL.md vs CLAUDE.md vs STATE.md]]

---

## O que mudou hoje

### 1. Refator `squads/` → `times/`

Conceitualmente passamos a tratar **áreas da empresa como Times**, e **sub-áreas como Squads**. A pasta `squads/` foi renomeada `times/` no monorepo. Hierarquia conceitual:

```
Stamper
  └── Time (área da empresa)
        └── Squad (sub-área)
              └── Squad aninhado (mais específico — opcional)
                    └── conteúdo (workers, skills, memory, context)
```

**Profundidade variável.** 3 níveis se a sub-área é monolítica. 4 níveis quando o Squad tem agrupamento natural com sub-squads de ritmo independente.

### 2. Path achatado no filesystem

Cada nível do path = um nível semântico. Não repetir `times/` ou `squads/` aninhado:

```
times/
├── infra/                              ← Time
├── marketing/                          ← Time
│   ├── conteudo/                       ← Squad
│   │   ├── insight-artificial/         ← Squad aninhado
│   │   ├── site-pd/                    ← Squad aninhado
│   │   └── workers/                    ← workers do Squad pai
│   ├── brand/                          ← Squad direto
│   └── performance/                    ← Squad direto (?)
├── dev/                                ← Time
│   ├── vitor/                          ← Squad (persona)
│   ├── amelia/                         ← Squad (persona)
│   └── ...
└── produto/                            ← Time
    ├── ferramentas-ia/cadencia/        ← Squad agrupador → Squad
    │   ├── frontend/                   ← Sub-squad
    │   ├── growth/                     ← Sub-squad
    │   └── ...
    ├── nskin/                          ← Squad (monolítico)
    ├── gci-go/                         ← Squad
    │   └── components/lara,ecuro,confirmacao-agenda/
    └── consultorias/
        ├── nathalia/
        └── padaria-milionaria/
```

**Identificação automática:** scripts (`render-html.py`, `_lookup_backends/`) detectam Squads procurando subpastas com `CLAUDE.md` — funciona em qualquer profundidade.

### 3. Memory em qualquer nível com CLAUDE.md

Regra simples: **tem `CLAUDE.md`? Tem `memory/`. Sem `CLAUDE.md`? Estado vive no pai.**

| Nível | Tem `memory/`? |
|---|---|
| Stamper | ✅ (memória pessoal Felipe — auto-memory) |
| Time | ✅ (STATE agregado dos Squads filhos + decisions transversais) |
| Squad | ✅ (STATE operacional + decisions específicas) |
| Squad aninhado | ✅ (STATE granular + decisions próprias) |
| Component | ❌ (estado vive no STATE do Squad pai) |
| Feature | ❌ (idem) |

Isso desfaz a regra anterior "Stamper não tem STATE.md". Agora **Time também tem STATE.md** — agregado a partir dos Squads filhos. Stamper continua sem STATE (a memória dele é a auto-memory pessoal do Felipe).

### 4. Agregação L1 híbrida determinística A+B+C

Time pai precisa saber estado dos Squads filhos. Squad pai precisa saber dos Sub-squads. **3 mecanismos**, **mesma função core** (`aggregate_l1(parent_path)` em `_core/state-aggregator.py`):

| Mecanismo | Como | Quando |
|---|---|---|
| **A** Manual | `/fechar-squad <squad>` propaga L1 pro Time pai | Felipe fecha sessão |
| **B** On-demand | `/abrir-squad <time>` calcula ao vivo (sem escrita) | Felipe abre Time |
| **C** Fallback cron | `state-aggregator.py --all --propagate` 03h BRT | Garantia que STATE Time nunca fica >24h stale |

Felipe disse: _"funciono bem fechando manualmente mas às vezes esqueço, então podemos ter as 3 versões no sistema. Mas precisa ser determinístico."_

Por isso **mesma função core** nos 3. Resultado consistente. Cron só reescreve se diff real (idempotente).

### 5. STATE inicial = onboarding doc

STATE.md inicial de cada Time/Squad é populado como **doc de onboarding** — o que um novo entrante na área precisaria pra começar a operar (igual onboarding de funcionário novo).

Template inicial: função, stack, pessoas-chave, projetos Linear vinculados, workflows ativos, docs relevantes, bloqueios externos, convenções. Pode ter overlap com `context/<x>.md` — STATE tem o **resumo onboarding**, `context/` tem **detalhes técnicos** profundos.

### 6. Personas podem habitar qualquer Time

Anterior (PDL-241): "personas BMAD/AIOX só em Dev + Maria Marketing + Diego Infra".

**Revisado:** personas BR podem habitar QUALQUER Time. Cada Time decide na sessão de criação quais personas fazem sentido. No Time Dev cada persona É um Squad. Em outros Times, persona pode ser Squad, Skill, ou inexistir.

### 7. Princípio "criar com Felipe"

Toda estruturação de Time/Squad nova é **trabalho conjunto**. Felipe é o único que conhece nuances do negócio (personas, sub-áreas com ritmo próprio, pessoas-chave, projetos Linear). Sem ele na sala, agente inventa estrutura que precisa redesenhar.

Padrão de sessão:
1. Apresentar o que se sabe (pastas reais, projetos Linear, INVENTORY refs)
2. Listar perguntas estruturadas (escopo, sub-squads, personas, workers, skills, pessoas-chave, Linear vinculados, bloqueios)
3. Felipe responde numerado
4. SÓ AÍ criar boilerplate

### 8. SOUL.md mantém escopo dos 4 produtos

| Produto | SOUL.md? |
|---|---|
| Cadência | ✅ |
| PD Portal | ✅ |
| NSkin | ✅ |
| GCI-GO | ✅ |
| Sub-squads, consultorias, Times operacionais | ❌ |

Será revisitado em cada sessão de criação — Felipe pode adicionar SOUL próprio em Marketing/Brand, Insight Artificial, ou consultorias se a voz delas for distinta.

---

## Tabela de Times pendentes

| Time | Status sessão de criação |
|---|---|
| Dev | ✅ Mapeado (8 personas BR como Squads) |
| Marketing | ⏳ Parcial (Conteúdo + Insight Artificial + Site PD + Brand identificados, sessão completa pendente) |
| Comercial | ⏳ Pendente |
| CS | ⏳ Pendente (sabemos: Squad Bot Telegram Suporte dentro) |
| Infra | ⏳ Atual populado antes da regra "criar com Felipe" — refator pendente |
| Operacional | ⏳ Pendente |
| Financeiro | ⏳ Pendente |
| Produto/Cadência | ⏳ Sessão própria (4 sub-squads mapeados) |
| Produto/PD Portal | ⏳ Pendente |
| Produto/NSkin | ⏳ Pendente |
| Produto/GCI-GO | ⏳ Pendente |
| Produto/Consultorias | ⏳ Sessão por cliente |

---

## Arquivos atualizados no repo

### Sessão tarde (memory híbrida)
- `_core/HIERARCHY.md` reescrito com Time/Squad/Sub-squad + path achatado
- `_core/memory-schema.md` reescrito com hierarquia memory + agregação A+B+C + onboarding template
- `_core/state-aggregator.py` criado — função `aggregate_l1()` determinística
- `times/infra/` (refator de `squads/infra/` — único Time populado pré-regra)
- `.githooks/pre-commit` ajustado pra novo path

### Sessão noite (integração Linear ↔ Squad — commits 416d571, 33d7d92)
- `_core/linear-squad-map.json` — 19/19 projetos Linear mapeados → Squads
- `_core/lib/squad_resolver.py` + `squad_integration.py` — helpers reutilizáveis
- `_core/SKILLS-LINEAR-INTEGRATION.md` — padrão completo
- `stamper/skills/criar-squad/` (nova) + `abrir-squad`/`fechar-squad` (atualizadas com mecanismos A/B)
- 8 skills Linear integradas em `stamper/skills/linear-*/`
- `stamper/skills/documentar/` (nova — persona Paula, Tech Writer)

### Sessão noite (foundation/ + constituição — commits d061441, 4701a84, 369b78f, aeb60d0)
- `_core/CRIACAO-TIME-BRIEFING.md` — Modo Foco + foundation/ + 9ª pergunta sobre foundation
- `_core/CONSTITUICAO-TIMES.md` — doc fundador (anatomia, foundation, lifecycle, sugestões por Time)
- `_core/memory-schema.md` ampliado com distinção memory ≠ foundation ≠ context
- `_core/HIERARCHY.md` menciona foundation/ na estrutura Time
- 3 memories migradas do auto-memory pra `stamper/memory/` versionada

### Bugs encontrados em validação end-to-end (commits 948d4a5, d6d6226)
- `squad_resolver.py` apontava pra credencial Linear errada → corrigido (`Linear - API` vault `Serviços & Tools` campo `password`)
- `register_project_in_state` inseria seção "Projetos Linear vinculados" no início do L3 empurrando conteúdo existente pra dentro → corrigido (insere no FIM do L3)

### Validações end-to-end (8/8 sub-testes passaram)
- ✅ `resolve_squad_from_project_id` em todos 19 projetos
- ✅ Cascata `resolve_squad_from_issue` via Linear API REAL (PDL-252 → stamper)
- ✅ `register_issue_in_state` + idempotência + update status
- ✅ `remove_issue_from_state` + idempotência
- ✅ `register_project_in_state` + idempotência (após fix)
- ✅ `propagate_after_close` (sem propagação pra REPO_ROOT — correto)

---

## Próximos passos (atualizado noite 25/05)

1. ✅ ~~Implementar `/fechar-squad` com propagação L1 (mecanismo A)~~ — feito
2. ✅ ~~Implementar `/abrir-squad <time>` com `aggregate_l1()` ao vivo (mecanismo B)~~ — feito
3. **Sessões de criação de Times, uma por uma, junto com Felipe** (próximo trabalho real)
4. Refator Time Infra (populado antes da regra)
5. Deploy do cron `state-aggregator.py --all --propagate` na VPS Master (mecanismo C) — PDL-252 criada, bloqueada por PDL-242 (Fase 7 deploy)

### Padrão pra abrir sessão de criação de Time (Modo Foco)

```
/criar-squad times/<area>

Modo: foco-criacao
Briefing: _core/CRIACAO-TIME-BRIEFING.md
```

Agente carrega APENAS o briefing (200 linhas) + Hierarchy + linear-squad-map filtrado. NÃO carrega INVENTORY/REFERENCE-*/PERSONAS inteiros. Reduz ~3-5k tokens iniciais vs 50k+.

### Constituição

Doc fundador que define em uma leitura o que é Time/Squad no framework:
- [[IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- Fonte canônica: `_core/CONSTITUICAO-TIMES.md`

---

## Referências

- Repo: `felipeluissalgueiro/pd-framework`
- Local: `Hub Projetos/pd-framework/`
- Linear projeto: PD Framework — Squads, Stamper, Memória Operacional
- Decisões anteriores: PDL-241 (Fase 0.7), PDL-218 (Fase 0)
