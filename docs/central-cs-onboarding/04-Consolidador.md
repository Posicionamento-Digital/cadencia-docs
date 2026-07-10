---
date: 2026-06-24
tags: [doc, componente, lib, crm, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[Ariane-Farrapo]]"]
---
# Consolidador (consolidador_onboarding + crm_onboarding)

## Identidade

- **Tipo:** lib Python (`_shared`)
- **Paths:** `_shared/consolidador_onboarding.py` (173 LOC) · `_shared/crm_onboarding.py` (245 LOC)
- **Status:** 🟢 produção (DEV-814)

## O que é

Orquestrador determinístico do onboarding pós-fechamento. Encadeia contrato → Asaas → CRM → tenant → Manual PDF. Idempotente, não-trava (cada passo isolado em try/except → vira pendência no checklist), `dry_run=True` por default.

## Passos

1. **contrato** — `find_contrato(slug)` + `parse_contrato(path)` (frontmatter: asaas_customer_id, parcelas, créditos, cliente, contrato, total).
2. **Asaas** — `asaas_reconcile.reconciliar(contrato, dry_run)` cria só o que falta.
3. **CRM** — `crm_onboarding.atualizar_crm`:
	- busca contato por **busca progressiva** (nome completo → 1º+último → só 1º nome, único)
	- lifecycle → `customer` + temperatura `quente`
	- opp `pd-onboarding` → stage `kickoff` (resolvido por id do pipeline)
	- nota-espelho idempotente (tag `[consolidador:espelho-contrato]`)
4. **tenant + registros** — `onboarding_provision.provisionar_onboarding`.
5. **Manual (Doc B)** — `doc_generator.gerar_manual_cliente` → PDF.
6. **alerta** — WhatsApp pro Felipe via Evo.

## Quickstart

```bash
python _shared/consolidador_onboarding.py ariane-farrapo 6bb2c1ba-7fb3-416a-b523-7c9561ea8db3
python _shared/consolidador_onboarding.py ariane-farrapo 6bb2c1ba-7fb3-416a-b523-7c9561ea8db3 --apply --notificar --alerta-para 5511914912127
```

## Don'ts

- Não chamar do receiver — sempre enfileirar job `consolidador`.
- Não passar `notificar=True` em dry_run (não envia, mas a intenção fica confusa).
- Não duplicar a nota-espelho manualmente — tag de idempotência.

## Relacionadas

- [[03-Consumer]] (chama via `_job_consolidador`)
- [[05-Doc-Generator]] (gera Manual)
- [[07-Evo-Client]] (alerta)
