---
date: 2026-06-20
tags: [dev, processo, linear]
moc: "[[MOC-Dev]]"
---
# Processo — Desenvolvimento (Time Dev / PD)

> Como nasce e anda uma entrega de software na PD: do projeto à story em produção. Cada etapa tem **dono** (persona do Time Dev) e **template canônico**. Fonte viva no framework: `pd-framework/_core/DEV-WORKFLOW.md` + `times/dev/CLAUDE.md`.

## Visão geral

Todo trabalho de dev passa por uma **cascata determinística**. Para **produto técnico** (team Linear **CAD**), a esteira completa é:

```
/linear-criar-projeto  →  Brief        (Paloma · PO)
        →  /linear-prd  →  PRD          (Paloma escreve)  +  Epics (Vitor · arquiteto)
        →  /linear-planejar-issue (EPIC) →  Stories        (Paloma · refinement)
        →  /linear-start-issue  →  codar  →  reviews §6  →  /linear-close-issue
```

Regra de ouro: **PRD existe antes de Epic; Epic antes de Story.** Nada de codar solto — o hook conta edições sem issue e manda parar.

**Cliente / CS** (team **COM**) NÃO usa PRD — segue a esteira de **12 fases CRM-PD**. Operação (team **OPS**) usa tarefa operacional.

## Etapas, donos e templates

| Etapa | Skill | Dono (persona) | Artefato + template |
|---|---|---|---|
| Criar projeto + **Brief** | `/linear-criar-projeto` | **Paloma** (PO) | Projeto Linear (template de projeto) + Linear Document *Brief* |
| **PRD** (Brief → PRD) | `/linear-prd` | **Paloma** | Linear Document *PRD* (problema, escopo, requisitos, stories previstas) |
| **Epics** (PRD → Epics) | `/linear-prd` | **Vitor** (Tech Lead) | Issues *Epic* (template Feature/Story + label `epic`) |
| **Stories** (Epic → Stories) | `/linear-planejar-issue` | **Paloma** | Sub-issues *Story* (mesmo template + label `story`), vertical slices ≤2 dias |
| Plano técnico da Story | `/linear-planejar-issue` | **Vitor** (gate) → **Amélia** | Plano + repo + branch `feat/<ID>` |
| Executar | `/linear-start-issue` → codar | **Amélia** / dev externo | Branch com o ID da issue (webhook Linear) |
| Fechar | `/linear-close-issue` | **Amélia** / **Vitor** | Merge na branch de produção + Done + deploy |

> Os templates são lei (nunca improvisar): projeto = templates do Linear; issue = Feature/Story · Bug · Chore; documento = Brief · Briefing · PRD.

## Modos de execução (sempre perguntar)

Ao iniciar **qualquer epic/story**, o agente pergunta ao Felipe: **Modo A ou Modo B?** Nunca assume.

- **Modo A — sequencial** (default em 95%): 1 executor por vez, **Amélia audita** cada diff. Usar quando há arquivos compartilhados, risco de conflito, ou decisão durante a execução.
- **Modo B — paralelo**: N executores em N branches, Amélia faz babysitting de todos. Só quando as stories são disjuntas (matriz de arquivos declarada). **Nunca** em migration / schema / auth / billing.

Em **ambos**: Amélia audita (babysitting não é exclusivo do B), **gate do Vitor** aprova o plano antes de executar, **cap de 3 ciclos** de fix por subagente (esgotou → escala pro Vitor ou Felipe).

## Reviews — obrigatórios, parte da auditoria

Auditar = revisar o diff **+ rodar as skills de review aplicáveis**. Babysitting sem as skills não conta como auditado.

| Tipo de mudança | Reviews |
|---|---|
| Trivial (copy, CSS isolado) | Nenhum formal — só Amélia revisa o diff |
| Código novo de feature | `/openrouter-review` |
| Bug difícil | `/openrouter-review` |
| Mudança lógica/funcional | `/runtime-fix-review` |
| **Crítica** (auth, billing, deploy, migração, RLS) | TODOS: `/claude-review` + `/dual-review` + `/runtime-fix-review` + Vitor + Felipe |
| Fim de epic (antes do merge final) | `/claude-review` + Vitor aprova |

Os reviews rodam via **OpenRouter**: **GLM 5.2** (obrigatório, primeiro) e, se inconsistente, escala pro **Qwen 3.7 Max** (`/openrouter-review`); `/dual-review` roda os dois sempre. Substituíram o Codex como review padrão.

## Gate de deploy — nunca subir sozinho

Agente trabalha a issue de ponta a ponta **mas PARA antes do deploy**:

1. Codar → reviews → babysitting.
2. **Abrir PR** (status → In Review) — nunca mergear/deployar direto.
3. **Notificar o Felipe no WhatsApp** com o link.
4. **Esperar autorização textual** do Felipe → só então merge → Done → deploy.

**cadencia-app / pd-portal** (Vercel Hobby): o merge de produção tem que ser feito pelo **owner** (`felipeluissalgueiro`) via `/aprovar-pr`, na branch **`master`** (não `main`). Detalhe: [[Processo - PR e Deploy na Vercel]].

## Documentação obrigatória (fim de feature)

Antes do merge final `feature → main`, a **Paula** (Tech Writer) roda `/documentar-software` — gera/atualiza a documentação no **cadencia-docs** (fonte de verdade cross-time). **Vitor** valida que a doc reflete a arquitetura real. Pula só em hotfix trivial.

## Personas do Time Dev

- **Vitor** — Tech Lead / arquiteto (gate técnico, fatia epics, aprova merge final)
- **Amélia** — Dev Sênior / orquestrador (babysitting, audita executores, merge de stories)
- **Paloma** — PO / Backlog (brief, PRD, refinement, critérios de aceite, quebra de stories)
- **Sofia** — UX · **Camila** — QA · **Paula** — Tech Writer (docs)
- **João** — challenge transversal (segunda opinião) · **Bruno** — POC rápido descartável

## Pessoas e ambientes

- **Felipe** — decisão estratégica, executor multi-frente, dono do merge de produção.
- **Luiz** — executor humano (escopo: `cadencia-app` + `pd-portal`). Tem **framework de dev próprio** na VPS Dev (`/home/luiz/.agents`, fluxo `to-prd`/`to-issues`), separado do pd-framework.

## Notas relacionadas

[[Processo - PR e Deploy na Vercel]]
