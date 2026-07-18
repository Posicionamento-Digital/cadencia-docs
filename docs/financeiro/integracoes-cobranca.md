---
title: Integrações de Cobrança — Stripe / Asaas
tags: [financeiro, canon]
---

# Integrações de Cobrança — Stripe / Asaas (+ lifecycle CRM Cadencia)

> Quando usar cada gateway, escopo de cada um e ponteiros pro código real (não duplicar).
> O lifecycle de billing (`payment`, `overdue`, `churn`) das marcas PD vive em `contacts` no CRM Cadencia. A cobrança financeira usa Stripe ou Asaas.

---

## Decisão rápida

| Cenário | Gateway |
|---|---|
| PD Consultorias / Gestores IA (cobrança lead→cliente) | **Stripe** (novo) / **Asaas** (recorrência legada). Lifecycle de billing no CRM Cadencia `contacts` — ⏳ CAD-600 |
| Cadência SaaS (B2C, checkout direto no produto) | **Stripe** |
| Novo cliente B2B BR/intl pós-2026-05-11 | **Stripe** |
| Cobrança recorrente B2B legada (pré-migração) | **Asaas** (descontinuação) |
| Cliente internacional (USD/EUR) | **Stripe** |

---

## CRM Cadencia — lifecycle de billing

- **Uso:** lifecycle de billing (payment/overdue/churn) lead→cliente das marcas PD Consultorias e Gestores IA, vivendo em `public.contacts` no CRM Cadencia.
- **Status:** CRM Cadencia é a fonte operacional do lifecycle; validar o gateway por cliente antes de criar cobrança nova.
- **Cobrança financeira:** NÃO é feita aqui — segue pelos gateways Stripe (novo) ou Asaas (recorrência legada).
- **Backend:** Supabase ref `elefbabxkaigusjiiflu` (produção = branch `master`); tenant PD `6bb2c1ba-7fb3-416a-b523-7c9561ea8db3`.
- **Endpoints:** `/api/app/contacts` e rotas financeiras do CRM.

---

## Stripe

- **Uso:** Cadência SaaS (B2C) + nova padrão BR/intl pós-2026-05-11.
- **Decisão:** Stripe é o gateway da Cadencia; Asaas permanece onde o contrato do cliente exigir.
- **Credencial:** 1Password vault `databases` ou similar — consultar mapa.
- **Código real:** integração já implementada na Cadência. Reusar:
  - **Checkout:** `Hub Projetos/Projetos BMAD/Cadencia/cadencia-growth/` (frontend SaaS)
  - **Workers (webhook, cobrança recorrente, retry):** `Hub Projetos/Projetos BMAD/Cadencia/cadencia-workers/`
  - **NUNCA duplicar a integração.** Pra novo caso de uso, importar/parametrizar o cliente Stripe existente.
- **Espelho de lifecycle:** webhooks Stripe atualizam o cliente no CRM Cadencia (`contacts`).

---

## Asaas

- **Uso:** legado em descontinuação. Manter operação até zerar cobranças recorrentes antigas.
- **Não usar em cobrança nova.** Toda cobrança nova vai Stripe (Asaas só mantém recorrências legadas até zerarem).
- **Credencial:** 1Password.
- **Código real:** wrapper Asaas em `Hub Projetos/Projetos BMAD/Cadencia/cadencia-workers/` (em fase de remoção conforme clientes migram).
- **Migração:** mapear clientes recorrentes Asaas ativos → migrar pro Stripe (lifecycle de billing acompanha no CRM Cadencia — ⏳ CAD-600).

---

## Regras absolutas

1. **Credencial só via 1Password.** Nunca em `.env`, código, logs ou notas.
2. **Não duplicar integração.** Stripe/Asaas já têm cliente implementado na Cadência — reusar.
3. **Webhook é fonte da verdade.** Não consultar status de cobrança via polling se webhook resolve.
4. **Validar gateway antes de cobrança nova.** O gateway varia por cliente.
5. **Reconciliação cruza os 3.** Ver `reconciliacao-bancaria.md` (EM REVISÃO).

---

## Refs

- `Hub Projetos/Projetos BMAD/Cadencia/cadencia-workers/` — workers Stripe/Asaas
- `Hub Projetos/Projetos BMAD/Cadencia/cadencia-growth/` — checkout Stripe
- `Hub Projetos/Credenciais/mapa-1password.md` — credenciais
- `ciclo-faturamento.md` — onde cobrança entra no fluxo
