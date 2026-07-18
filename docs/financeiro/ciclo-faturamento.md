---
title: Ciclo de Faturamento
tags: [financeiro, canon]
---

# Ciclo de Faturamento PD

> Fluxo end-to-end: lead → cliente → cobrança → recebimento → NF → reconciliação.
> Esta é a ordem operacional — qualquer asset financeiro respeita essa sequência.

---

## Visão geral

```
[Lead] → [Fechamento Comercial] → [Contrato] → [Cobrança] → [Recebimento] → [NFSe] → [Reconciliação] → [DRE]
   ↑                                              ↓
Marketing/Comercial                  Stripe / Asaas (gateways) + CRM Cadencia (lifecycle)
```

---

## Etapas

### 1. Lead → Fechamento (responsabilidade: Time Comercial)

- Lead chega via Marketing → pipeline Comercial → fechamento.
- **Output pro Financeiro:** dados do cliente (nome, CNPJ/CPF, endereço fiscal, valor, recorrência, trilha).
- Não há "passagem de bastão formal" — Comercial atualiza ficha do cliente no CRM.

### 2. Contrato (responsabilidade: Financeiro + Comercial)

- Modelo do contrato escolhido conforme trilha — ver `contratos-modelo.md`.
- Contrato assinado vira instância em PDF arquivado (hoje: dispersa; backlog: indexar).
- **Gatilho pra próxima etapa:** contrato assinado.

### 3. Cobrança (responsabilidade: Financeiro)

- Gateway escolhido conforme produto — ver `integracoes-cobranca.md`.
- **PD Consultorias / Gestores IA:** lifecycle de billing no CRM Cadencia (`contacts`); cobrança financeira via gateway (Asaas/Stripe).
- **Cadência SaaS:** Stripe (direto no produto — Squad Cadência opera).
- **Recorrência B2B legado:** Asaas (em descontinuação).
- **Frequência:** conforme contrato (mensal padrão, anual eventual com desconto).

### 4. Recebimento (Financeiro)

- Confirmação no gateway → webhook ou consulta manual.
- Lançamento em planilha de Contas a Receber.
- Inadimplência: notificação automática primeiro (Stripe + lifecycle `payment/overdue/churn` no CRM Cadencia) → cobrança ativa em D+7 → suspensão acesso em D+15 → encerramento em D+30.

### 5. Emissão NFSe (Financeiro)

- Gatilho: recebimento confirmado.
- Prazo: até dia 5 do mês subsequente.
- Regras em `politica-fiscal.md`.
- Output: NF arquivada em pasta do cliente + enviada por email.

### 6. Reconciliação (Financeiro)

- Frequência: semanal (backlog cron) / mensal (hoje manual).
- Cruza extratos bancários + faturas cartões + comprovantes + recebimentos do gateway.
- Doc: `reconciliacao-bancaria.md` (EM REVISÃO — backlog).

### 7. Registro DRE (Financeiro)

- Lançamento mensal por trilha (Consultorias / Gestores IA / Cadência).
- Apura margem por cliente/produto.
- Doc: `dre-structure.md` (EM REVISÃO).

---

## SLAs internos

| Etapa | SLA |
|---|---|
| Contrato → primeira cobrança | 24h após assinatura |
| Recebimento → NFSe emitida | Até dia 5 do mês subsequente |
| Recebimento → registro DRE | Mensal (fechamento até dia 10) |
| Inadimplência → ação | D+7 cobrança ativa / D+15 suspensão / D+30 encerramento |

---

## Bloqueios atuais

- **Lifecycle no CRM Cadencia:** validar gateway (Asaas/Stripe) por cliente antes de criar nova cobrança.
- **DRE em planilha:** sem sistema estruturado — risco de divergência.
- **Contratos dispersos:** PDFs por cliente não indexados — dificulta auditoria.

---

## Refs

- `integracoes-cobranca.md` — gateways
- `politica-fiscal.md` — NFSe
- `contratos-modelo.md` — modelos
- `dre-structure.md` — registro contábil
