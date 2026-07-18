---
title: Fluxo de Caixa
tags: [financeiro, canon]
---

# Fluxo de Caixa — PD

> Projeção de caixa 90 dias, cálculo de runway e burn mensal.
> Operacional caixa de Bárbara (CFO). Toda decisão de gasto estrutural passa por aqui.

---

## Princípio

Runway > 12 meses → opera com confiança.
Runway 6-12 meses → cuidado, sem gasto estrutural novo.
Runway 3-6 meses → modo defensivo, corte + foco em receita.
Runway < 3 meses → emergência, decisões diárias.

**Bárbara olha runway TODA semana.**

---

## Estrutura da projeção (modelo)

| Mês | Saldo inicial | Receita prevista | Despesa prevista | Saldo final |
|---|---|---|---|---|
| M+0 (atual) | R$ _______ | R$ _______ | R$ _______ | R$ _______ |
| M+1 | (saldo M+0) | R$ _______ | R$ _______ | R$ _______ |
| M+2 | (saldo M+1) | R$ _______ | R$ _______ | R$ _______ |
| M+3 | (saldo M+2) | R$ _______ | R$ _______ | R$ _______ |

### Receita prevista (por trilha)

```
Mês M+N:
  + MRR recorrente (Consultorias + Gestores IA + Cadência SaaS)
  + Receita projetada de fechamentos no mês (pipeline × taxa fechamento)
  + Recebimentos parcelados em aberto
  - Churn projetado
  = Receita prevista total
```

### Despesa prevista (por categoria)

```
Mês M+N:
  + Despesas fixas confirmadas (infra, ferramentas, PJ recorrente, pró-labore)
  + Despesas variáveis estimadas (APIs, marketing, infra elástica)
  + Compromissos não-mensais alocados (impostos trimestrais, contador, anuais)
  = Despesa prevista total
```

---

## Métricas

### Burn mensal

```
Burn = Despesa total - Receita total  (no mês)
```

- Burn positivo = está queimando caixa
- Burn negativo = está lucrando (caixa cresce)

### Runway

```
Runway (meses) = Saldo atual / Burn mensal médio (últimos 3 meses)
```

Se burn é negativo (lucro): runway = ∞ (não há queima).

### Margem operacional

```
Margem operacional = (Receita - Despesa) / Receita × 100
```

PD deve manter > 30% como meta — abaixo disso, ajustar pricing ou cortar custo.

---

## Cenários (toda projeção tem 3)

| Cenário | Premissa |
|---|---|
| **Base** | Pipeline atual converte na taxa histórica, churn conhecido, sem investimento novo |
| **Otimista** | Pipeline +30%, churn -20%, MRR +15% por upsell |
| **Pessimista** | Pipeline -30%, churn +50%, perda 1 cliente grande |

Bárbara decide olhando o pessimista. Se runway no pessimista < 6 meses, **pausar gasto estrutural novo**.

---

## Cadência de atualização

| Atividade | Frequência |
|---|---|
| Saldo atual | Diária (saldo dos bancos) |
| Receita do mês corrente | Semanal (pós-reconciliação) |
| Projeção 90d | Mensal (fechamento do mês) |
| Projeção 12 meses | Trimestral |
| Cenário pessimista | Mensal (mínimo) |

---

## Regras

1. **Saldo é caixa real (banco), não receita reconhecida.** Cliente pode ter contratado e ainda não pago — só entra no caixa quando o dinheiro está na conta.
2. **Despesa é compromisso assumido**, não só pago. Boleto cartão de R$ 50k a vencer em D+15 já entra no fluxo.
3. **Sempre 3 cenários.** Nunca decidir só com o cenário base.
4. **Runway < 6 meses (pessimista) → modo defensivo.** Bárbara avisa Felipe imediatamente.
5. **Pró-labore Felipe entra no fluxo.** Mesmo que variável.
6. **Receita Cadência (Stripe direto):** consultar dashboard Cadência — não é a mesma cobrança das outras trilhas.

---

## Backlog (skill /projecao-runway futura)

Worker que:
- Lê saldo atual dos bancos (manual upload ou Open Finance)
- Lê MRR e churn do dashboard Cadência + extrato Stripe/Asaas
- Calcula 3 cenários (base/otimista/pessimista) com runway de cada
- Gera alerta automático se pessimista < 6 meses
- Cadência: mensal (fechamento)

---

## Refs

- `dre-structure.md` — composição receita/despesa
- `reconciliacao-bancaria.md` — fonte do saldo real
- `precificacao-margens.md` — base do MRR
- `ciclo-faturamento.md` — quando receita vira caixa
- Pasta local: `Finanças/financeiro/fluxo-de-caixa/`
