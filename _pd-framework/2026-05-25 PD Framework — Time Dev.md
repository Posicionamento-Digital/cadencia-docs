---
date: 2026-05-25
tags: [ia, framework, pd, time, dev, personas, bmad]
moc: "[[MOC-Conhecimento]]"
---

# PD Framework — Time Dev

> Documentação humana do bootstrap. Fonte canônica: `pd-framework/times/dev/`
> Linear: **PDL-256** (bootstrap, Done)
> Commits: `bff6aa9` (estrutura completa) + `988a1d3` (L1 propagation)

---

## Função do Time

Cobre **desenvolvimento de software dos produtos PD** (Cadência, PD Portal, NSkin, GCI-GO, Cadência-Contato, Consultorias customizadas) + skills/workers do framework + bugs/refactor/manutenção. **NÃO cobre:** infra/VPS/deploy (Time Infra/Diego), estratégia de produto (Marketing/Maria), processo comercial (Time Comercial), CS-ops (Time CS). Coordena com **Luiz** (executor humano, escopo limitado a `cadencia-app` + `pd-portal` — framework próprio futuro `pd-framework-luiz` PDL-225 Backlog Fase 6).

---

## Estrutura

```
times/dev/
├── CLAUDE.md                       (líder: Vitor)
├── foundation/                     (5 docs constitutivos)
│   ├── README.md                   (índice + regras de consulta)
│   ├── code-principles.md          ✅ populado (Clean Code adaptado PD)
│   ├── branch-convention.md        ✅ populado (luiz/feat/feature/main)
│   ├── padrao-commit.md            ✅ populado (Conventional + Closes PDL-XX)
│   ├── babysitting-checklist.md    ✅ populado (10 etapas)
│   └── padrao-testes.md            ⚠️ EM REVISÃO (Camila consolida)
├── skills/                         (4 skills)
│   ├── dev-debate.md               (party mode 8 personas, síntese Vitor)
│   ├── joao.md                     (challenger transversal, 5 eixos)
│   ├── paula.md                    (referência pra /documentar global)
│   └── bruno.md                    (modo opt-in dentro /linear-planejar-issue)
├── memory/
│   ├── STATE.md                    (L1/L2/L3 + L2 sub-squads agregado)
│   └── decisions.md                (append-only)
├── workers/                        (vazio — sem cron próprio do Dev)
├── context/                        (vazio — sessão dedicada futura)
├── vitor/                          (Squad — Tech Lead)
├── amelia/                         (Squad — Dev Senior Orquestrador)
├── paloma/                         (Squad — PO/Backlog)
├── sofia/                          (Squad — UX)
├── camila/                         (Squad — QA)
├── paula/                          (Squad — Tech Writer)
├── joao/                           (Squad — PM transversal)
└── bruno/                          (Squad — Quick-Dev opt-in)
```

Cada Squad de persona tem: `CLAUDE.md` detalhado (persona + Critical Actions + voz + escopo + anti-padrões) + `memory/STATE.md` L1/L2/L3 onboarding + `memory/decisions.md` append-only + pastas `skills/`/`workers/`/`context/` (vazias, sessão dedicada futura).

---

## Personas (8 Squads)

| Persona | Squad | Inspiração BMAD/AIOX | Voz |
|---|---|---|---|
| **Vitor** | `times/dev/vitor/` | Winston (BMAD Architect) | Tech Lead. "Qual a invariante a preservar?" Decide arquitetura, gate técnico, aprova merge `feature → main`. |
| **Amélia** | `times/dev/amelia/` | Amelia/James (BMAD Dev) | Dev Senior Orquestrador. "Como subagente vai escorregar?" Babysitting, loop fix max 3 ciclos, merge stories em feature. |
| **Paloma** | `times/dev/paloma/` | Sarah (AIOX PO) | PO/Backlog Steward. "Qual a menor coisa que entrega valor?" Refinement, critérios de aceite, validação. |
| **Sofia** | `times/dev/sofia/` | Sally (BMAD UX) | UX. "Quantos cliques? Usuário entende sem ler?" Design, fluxo, micro-interações. |
| **Camila** | `times/dev/camila/` | Quinn (BMAD QA) | QA. "E quando input é null? E em mobile 3G?" Edge cases, reviews, consolidação de padrão de testes. |
| **Paula** | `times/dev/paula/` | Paige (BMAD Tech Writer) | Tech Writer. **Dona obrigatória da `/documentar`** §13 DEV-WORKFLOW. |
| **João** | `times/dev/joao/` | John (BMAD PM) | Challenger transversal. "E se não fizéssemos nada? Reversibilidade?" Invocável via `/joao` em 5 eixos. |
| **Bruno** | `times/dev/bruno/` | Barry (BMAD Quick-Dev) | Quick-Dev opt-in. "POC em 2h, descartável por default." Sugestão dentro `/linear-planejar-issue`. |

---

## Foundation docs (status)

| Doc | Status | Conteúdo principal |
|---|---|---|
| `code-principles.md` | ✅ populado | Clean Code adaptado: KISS/DRY/YAGNI, default zero comentários, trust internal code, "nunca declarar incompleto como concluído" |
| `branch-convention.md` | ✅ populado | Hierarquia `luiz/pdl-XX → feat/pdl-XX → feature/<f> → main`; nunca merge direto main |
| `padrao-commit.md` | ✅ populado | Conventional Commits + obrigatório `Closes PDL-XX` + HEREDOC pra preservar formatação |
| `babysitting-checklist.md` | ✅ populado | 10 etapas (sintaxe/imports/refs/paths/decisões/smoke/diff/hook/push/Linear) — origem `stamper/memory/feedback_babysitting_obrigatorio.md` |
| `padrao-testes.md` | ⚠️ EM REVISÃO | Sem prática consolidada PD hoje. Camila vai consolidar nos próximos sprints. Issue Linear a abrir. |
| `dev-workflow.md` | ❌ NÃO criado | Referência inline pra `_core/DEV-WORKFLOW.md` no README — evita duplicação |
| `boilerplate-templates.md` | ❌ NÃO criado | Só quando demanda real |

---

## Decisões-chave

- **2026-05-25** — 8 personas = 8 Squads diretos (3 níveis simples) — consistência > pragmatismo (PDL-241). Mesmo Bruno sendo modo opt-in vira Squad. Sub-aninhar dentro de persona seria overhead sem ganho.
- **2026-05-25** — Skills invocáveis individuais: só 3 transversais agora (`/joao`, `/paula` ref, `/bruno`). NÃO criar `/vitor`, `/amelia`, `/paloma`, `/sofia`, `/camila` — vivem dentro de fluxos (Camila no QA durante `/linear-close-issue`, Sofia consulta antes de design, etc). Pra invocar standalone: `/abrir-squad times/dev/<persona>`.
- **2026-05-25** — Foundation: 4 populados + 1 EM REVISÃO + 1 referência inline + 0 criado preventivo. `dev-workflow.md` apontou pra `_core/DEV-WORKFLOW.md` — fonte única, evita drift.
- **2026-05-25** — Workers/ vazios — Dev é horizontal, sem cron próprio. Workers Cadência/PD Portal pertencem aos Squads de Produto.
- **2026-05-25** — SRE/Security Engineer/Data Engineer descartados (PDL-241) — não reabrir.

---

## Pessoas-chave

- **Felipe** — decisões estratégicas, executor multi-frente
- **Luiz Sidião** — executor humano dev, escopo `cadencia-app` + `pd-portal`. VPS Dev `/home/luiz/`. Framework próprio futuro `pd-framework-luiz` (PDL-225 Backlog Fase 6).

Sem contratação prevista. Sem freela recorrente.

---

## Projetos Linear (executados pelo Time Dev, donos = Squads de Produto)

- **Cadência** (`times/produto/cadencia/`):
  - `prod: Cadência — Roadmap`
  - `maint: Cadência — Bugs e suporte`
- **Cadência Growth** (`times/produto/cadencia/growth/`):
  - `Cadência Growth — Separação de Repo + Migração Railway → VPS`
- **Cadência de Contato** (`times/produto/cadencia-contato/`):
  - `prod: cadência de contato Ceilândia e Plano Piloto`
- **PD Portal** (`times/produto/pd-portal/`):
  - `Portal de Clientes PD — Cadencia`

Time Dev **não é dono** desses projetos. Executa demanda neles via personas (Vitor planeja → Amélia executa → Paula documenta → Vitor aprova merge).

---

## Bloqueios externos

- **PDL-225** (Backlog Fase 6) — `pd-framework-luiz` em construção. Não bloqueia Dev hoje; impacta coordenação cross-framework futura.
- **PDL-242** (Fase 7) — Deploy pd-framework na VPS. Só relevante se Dev quiser cron próprio.

Sem bloqueio crítico ativo.

---

## 2 Modos de execução (regra absoluta)

Ao iniciar **QUALQUER** epic/story, agente SEMPRE pergunta ao Felipe: **"Modo A (sequencial + auditoria Amélia) ou Modo B (paralelo com babysitting Amélia)?"** Nunca assume default.

- **Modo A** — Linear sequencial (95% dos casos). 1 executor + Amélia auditando cada diff.
- **Modo B** — Paralelo. N subagentes-executores em N branches simultâneas, Amélia audita todos.

Regras absolutas em AMBOS modos: gate Vitor antes Amélia executar · cap 3 ciclos de fix · Modo B NUNCA em migration/schema/auth/billing.

Detalhes: `_core/DEV-WORKFLOW.md §2-§5`.

---

## Como usar

- **Abrir Time:** `/abrir-squad times/dev`
- **Abrir Squad de persona:** `/abrir-squad times/dev/vitor` (ou amelia/paloma/sofia/camila/paula/joao/bruno)
- **Debate multi-persona:** `/dev-debate` — roundtable 8 personas, síntese Vitor
- **Challenger:** `/joao` — segunda opinião transversal em 5 eixos
- **Documentar feature:** `/documentar <feature-path>` (Paula é dona)
- **Quick-Dev (opt-in):** dentro de `/linear-planejar-issue` quando issue <4h

---

## Pendências pra sessões futuras

- **Camila consolida `foundation/padrao-testes.md`** — abrir issue Linear própria, 2-3 sprints
- **Skills individuais por persona** (`/vitor`, `/amelia`, etc) — só criar se Felipe sentir falta em fluxo real (decisão atual: vivem dentro dos Squads)
- **Workers cron Dev** se nascer demanda (hoje pasta vazia)
- **`boilerplate-templates.md`** se virar demanda recorrente (templates de skill/worker)
- **Label `squad:times/dev`** criada via MCP — aplicada em PDL-256

---

## Notas relacionadas

- [[IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada]]
- [[IA-Tecnologia/2026-05-25 Stamper — Chief of Staff PD Framework]]
