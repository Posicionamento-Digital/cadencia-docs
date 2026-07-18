---
title: Precificação e Margens
tags: [financeiro, canon]
---

# Precificação e Margens — PD

> Política de preço, métricas SaaS (CAC/LTV/LHI/Payback), política de desconto.
> Toda decisão de pricing passa por aqui antes de virar oferta comercial.

---

## Princípio

**Preço não é negociação — é decisão.** Preço da PD é função de:
1. Custo direto da entrega (infra + APIs + pessoas)
2. Margem alvo por trilha
3. Posicionamento da marca (PD não é commodity)
4. Capacidade de fila (capacidade limitada justifica preço alto)

Desconto é exceção, não regra. Toda exceção é registrada (cliente, motivo, valor original × concedido).

---

## Métricas SaaS — definições operacionais

### CAC (Customer Acquisition Cost)

```
CAC = (Gasto marketing + Gasto comercial) / Clientes novos no período
```

- Calculado **por trilha** (não agregado)
- Inclui: ads pagos, custo ferramentas marketing, custo PJ comercial alocado
- Exclui: pró-labore Felipe (a menos que aloque % comercial específico)

### LTV (Lifetime Value)

```
LTV = Ticket médio × Margem bruta % × Tempo médio de vida (meses)
```

- Calculado **por trilha**
- "Tempo médio de vida" = 1 / churn mensal

### Payback CAC

```
Payback (meses) = CAC / (Ticket médio × Margem bruta %)
```

Meta: **payback < 6 meses** por trilha.
Payback > 12 meses → repensar pricing OU custo aquisição.

### LHI (Lifetime Health Index — métrica PD)

```
LHI = LTV / CAC
```

- LHI > 3 → saudável
- LHI 1-3 → marginal, revisar
- LHI < 1 → trilha está destruindo valor, parar de adquirir

### Churn

```
Churn mensal = Clientes que cancelaram no mês / Clientes ativos no início do mês × 100
```

- Calculado **por trilha**
- Meta PD: < 5% mensal (SaaS) / < 8% (consultorias high-touch)

---

## Política de preço por trilha (EM REVISÃO — Felipe preenche)

### PD Consultorias
- Modelo: _______
- Faixa de preço: R$ _______
- Margem alvo: ___ %
- Desconto máximo permitido sem aprovação: ___ %

### PD Gestores de IA
- Modelo: _______
- Mensalidade: R$ _______
- Margem alvo: ___ %
- Desconto programa antecipado / pagamento à vista: ___ %

### Cadência SaaS
- Planos: _______
- MRR alvo por cliente: R$ _______
- Margem alvo: ___ % (SaaS típico > 70%)
- Política trial: _______
- Política upgrade/downgrade: _______

---

## Política de desconto

| Situação | Desconto permitido | Quem aprova |
|---|---|---|
| Pagamento à vista (anual) | Até 15% | Bárbara |
| Múltiplas trilhas (cross-sell) | Até 10% | Bárbara |
| Cliente estratégico (case, indicação) | Caso a caso | Felipe |
| Desconto fora dessas regras | — | Felipe + Bárbara em debate |

**Toda concessão é registrada** em `decisions.md` com cliente, motivo, valor original × concedido.

---

## Ajuste de preço (reajustes)

### Inflação anual
- Reajustar contratos recorrentes em **janeiro** pelo IGP-M ou IPCA dos 12 meses
- Aviso prévio: 30 dias antes
- Cliente pode optar por antecipar pagamento com preço antigo (até 12 meses)

### Reposicionamento (mudança discricionária)
- Aplicar apenas a **novos clientes** (não retroativo)
- OU aplicar pra base com aviso prévio 90 dias + transição de 3 meses
- Decisão sempre via `/financeiro-debate`

---

## Plano econômico (cliente fora do ICP)

Cliente que não cabe no ICP comercial mas pede atendimento:
- Opção 1: oferecer plano econômico (Cadência B2C) sem consultoria
- Opção 2: encaminhar pra concorrente / parceiro (NÃO atender abaixo do custo)
- Opção 3: lista de espera (se fila estiver cheia)

**NUNCA atender abaixo do custo só pra fechar.** Cliente abaixo do custo destrói margem e ocupa capacidade.

Ver `anti-icp-financeiro.md`.

---

## Backlog

- Calcular CAC/LTV/LHI por trilha (precisa dado histórico + alocação de marketing)
- Definir margem alvo por trilha (depende DRE)
- Política de reajuste 2027 (decidir em Q4/2026)

---

## Refs

- `dre-structure.md` — composição de custos por trilha
- `anti-icp-financeiro.md` — quando não atender
- `ciclo-faturamento.md` — onde preço entra
- `contratos-modelo.md` — preço em cláusula contratual
- `fluxo-caixa.md` — impacto pricing em runway
