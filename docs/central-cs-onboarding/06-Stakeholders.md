---
date: 2026-06-24
tags: [doc, componente, lib, crm, raci, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[financeiro]]"]
---
# Stakeholders + Matriz RACI + Form Tally

## Identidade

- **Tipo:** lib Python (`_shared`)
- **Paths:** `_shared/stakeholders.py` (223) · `matriz_responsabilidades.py` (382) · `tally_form_stakeholders.py` (134)
- **Status:** 🟢 produção (DEV-799)

## Papéis canônicos (FIXOS)

| slug | label |
|---|---|
| `decisor` | Decisor |
| `owner_ia` | Owner da IA |
| `gestor_trafego` | Gestor de tráfego |
| `operacional` | Operacional |
| `financeiro` | Financeiro |
| `ti` | TI |

Aliases via `normalize_role(value)`: "owner da ia", "trafego", "decision maker", "operações", etc.

## Fluxo de ingestão

1. Valida `papel_canonico` antes de tocar o CRM (lista FIXA).
2. Empresa: `companies search` → `companies create --razao-social --nome-fantasia [--setor]`.
3. Pra cada stakeholder:
	- `contacts search` (dedup por email/tel/nome)
	- `contacts create --first-name --last-name --email --phone --lifecycle customer`
	- `contacts link-company <id> --company <comp> --role <papel>`
	- nota relacionando ao decisor (exceto no próprio decisor)

`dry_run=True` default — `plan.commands` mostra a sequência sem executar.

## Matriz RACI por produto

Fonte ÚNICA em `matriz_responsabilidades.py`. Lista PD / cliente / gestor_trafego por produto. Consumida pelo Checklist de Responsabilidades + bloco `{{itens_especificos_produto}}` do Doc A.

Espelho legível: `times/cs/foundation/matriz-responsabilidades.md` (manter sincronizado — .py é canônico).

## Form Tally

`python _shared/tally_form_stakeholders.py "Stakeholders — <cliente>"` cria form com 6 slots (1º obrigatório = decisor). Submissão ingerida pelo handler Tally (DEV-808) → plugada em `ingest_stakeholders()`.

## Don'ts

- Não inventar papel novo.
- Não rodar `dry_run=False` sem revisar `plan.commands`.
- Não duplicar a matriz em código Python — só em md espelho.

## Relacionadas

- [[03-Consumer]] · [[05-Doc-Generator]] (matriz vira `{{itens_especificos_produto}}`)
