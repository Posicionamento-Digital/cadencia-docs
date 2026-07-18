---
title: Reconciliação Bancária
tags: [financeiro, canon]
---

# Reconciliação Bancária — PD

> Como cruzar extratos bancários + faturas de cartões + comprovantes + recebimentos de gateway para fechar o mês sem furo.

---

## Princípio

Toda movimentação financeira da PD aparece em **4 lugares simultaneamente**. Se um lugar diverge dos outros, tem erro. Reconciliação semanal = pegar divergência cedo, antes de virar buraco.

```
[Gateway: Stripe/Asaas]  ← receita / cobrança
        ↕
[Extrato bancário]           ← entrada / saída real
        ↕
[Faturas cartão]             ← despesas operacionais
        ↕
[Comprovantes pagamento]     ← lastreio dos lançamentos
```

---

## Fontes (todas hoje em pasta local)

| Fonte | Path | Cadência |
|---|---|---|
| Extratos bancários | `ClaudeCode/Finanças/financeiro/extratos/` | Mensal (PDF) |
| Faturas cartões | `ClaudeCode/Finanças/financeiro/faturas cartões/` | Mensal (PDF) |
| Comprovantes | `ClaudeCode/Finanças/financeiro/comprovantes/` | Por transação |
| Recebimentos Stripe | Dashboard Stripe + webhook (Cadência) | Real-time |
| Recebimentos Asaas | Dashboard Asaas | Real-time (descontinuação) |

---

## Processo de reconciliação (semanal)

### 1. Receita (recebimentos)

Pra cada gateway:
1. Listar transações da semana (data, valor, cliente, status)
2. Cruzar com extrato bancário (data de crédito + valor)
3. Marcar conciliado se bate
4. Flagar divergência:
   - **Cobrado mas não recebido** → seguir D+7 (ver `ciclo-faturamento.md` inadimplência)
   - **Recebido mas não cobrado** → erro de lançamento, investigar
   - **Valor diferente** → tarifa de gateway (esperado) ou erro

### 2. Despesas (saídas)

1. Listar despesas do extrato + faturas cartão da semana
2. Cruzar com comprovantes na pasta
3. Categorizar (infra, APIs, marketing, ferramentas, PJ, admin)
4. Flagar:
   - **Despesa sem comprovante** → pedir nota fiscal / recibo do fornecedor
   - **Despesa fora de padrão** → review com Bárbara (CFO)
   - **Cobrança duplicada** → contestar (fornecedor ou banco)

### 3. Fechamento (mensal)

- Soma receita líquida do mês por trilha
- Soma despesa total por categoria
- Calcula margem por trilha (ver `dre-structure.md`)
- Atualiza fluxo de caixa (ver `fluxo-caixa.md`)
- Output: planilha mensal arquivada em `Finanças/financeiro/fluxo-de-caixa/`

---

## Regras

1. **Reconciliação é semanal — não mensal.** Mensal acumula erro silencioso.
2. **Toda divergência é registrada** — mesmo que resolvida no mesmo dia. Histórico de erro ajuda a achar padrão.
3. **Tarifa de gateway é esperada** — não confundir com erro. Stripe ~3.9%, Asaas ~2%.
4. **Despesa sem comprovante = pendência aberta.** Não fechar mês com pendência > 7d sem justificativa.
5. **Conta pessoal Felipe NÃO entra.** Só PJ PD.

---

## Backlog (skill /reconciliar-cobranca futura)

Worker que:
- Lê CSV/API dos 3 gateways
- Cruza com extrato bancário (Open Finance? upload manual?)
- Gera relatório de conciliação + flag divergências
- Sugere lançamento contábil por categoria
- Cadência: semanal (segunda 9h BRT)

---

## Refs

- `ciclo-faturamento.md` — onde recebimento entra no fluxo
- `integracoes-cobranca.md` — gateways
- `dre-structure.md` — alocação por trilha
- `fluxo-caixa.md` — projeção pós-reconciliação
- Pasta local: `Finanças/financeiro/` (todas as fontes hoje)
