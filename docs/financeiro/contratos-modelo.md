---
title: Contratos Modelo
tags: [financeiro, canon]
---

# Contratos Modelo — PD

> Ponteiro pros 3 contratos modelo no Obsidian Time PD + quando usar cada.
> **Fonte da verdade:** `Time PD/Financeiro/Contratos/`.

---

## Os 3 contratos

### 1. Contrato Agente IA

- **Arquivo:** `Time PD/Financeiro/Contratos/Contrato-Agente-IA.md`
- **Quando usar:** cliente contratando agente de IA white-label (ex: Lara para Grupo GCI, futuras franquias).
- **Características:**
  - Mensalidade recorrente
  - Inclui suporte técnico + atualizações + monitoramento operacional
  - Código NFSe: 115013000 (suporte em TI)
- **Gateway recomendado:** Stripe (novo) ou Asaas (recorrência legada). Lifecycle de billing no CRM Cadencia — ⏳ CAD-600.

### 2. Contrato Consultoria/Treinamento

- **Arquivo:** `Time PD/Financeiro/Contratos/Contrato-Consultoria-Treinamento.md`
- **Quando usar:** projeto de consultoria estratégica ou treinamento pontual.
- **Características:**
  - Projeto fechado (escopo + entregas + prazo)
  - Pagamento por marco / parcelado
  - Não recorrente
- **Gateway recomendado:** Asaas (parcelado) ou Stripe (one-time). Lifecycle de billing no CRM Cadencia — ⏳ CAD-600.

### 3. Contrato Jornada Gestor IA

- **Arquivo:** `Time PD/Financeiro/Contratos/Contrato-Jornada-Gestor-IA.md`
- **Quando usar:** programa Gestores de IA (formação + acompanhamento).
- **Características:**
  - Programa estruturado (módulos + duração)
  - Pagamento parcelado ou à vista com desconto
- **Gateway recomendado:** Asaas (parcelado) ou Stripe. Lifecycle de billing no CRM Cadencia — ⏳ CAD-600.

---

## Como escolher

```
Cliente quer um agente de IA pra rodar operação dele?    → Agente IA
Cliente quer projeto pontual / treinamento?              → Consultoria/Treinamento
Cliente quer entrar no programa Gestores IA?             → Jornada Gestor IA
```

---

## Regras

1. **Sempre usar modelo do Obsidian.** Não criar contrato do zero — adapta o existente.
2. **Personalizar:** valor, prazo, dados cliente, escopo.
3. **Não personalizar:** cláusulas jurídicas, foro, política de inadimplência (consultar contador/advogado se precisar mudar).
4. **Instância:** PDF assinado vai pra pasta do cliente (backlog: indexar).

---

## Backlog (issues filhas PDL-274)

- Indexar contratos assinados por cliente (hoje dispersos)
- Versionar mudanças nos modelos no Obsidian
- Avaliar criação de contrato Cadência B2B (se demanda surgir)

---

## Refs

- Obsidian: `Time PD/Financeiro/Contratos/` (fonte original dos 3 modelos)
- `ciclo-faturamento.md` — onde contrato entra no fluxo (etapa 2)
- `integracoes-cobranca.md` — gateway recomendado por contrato
