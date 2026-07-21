---
title: Programa de Revenda
tags: [comercial, revenda, canon]
---

# Programa de Revenda — Cadencia

> Documento canônico do canal de revenda. Fonte: `pd-framework/times/comercial/foundation/programa-revenda.md`.
> Criado em sessão guiada com Felipe (2026-07-21 — revendedor inaugural: Vayne Saccaro).

---

## Princípio

O revendedor não é um desconto — é um canal de distribuição.

Felipe executa e fecha; o revendedor distribui e indica. A margem de cada parte reflete o trabalho de cada parte. O revendedor ganha indicando clientes certos e abrindo portas — não executando projetos.

---

## Os dois modelos de parceria

### Modelo A — Revenda de créditos

**Quando usar:** cliente do revendedor usa o Cadencia de forma mais autônoma, sem implementação complexa. O revendedor vende acesso, não projeto.

**Como funciona:**

- O revendedor compra créditos para o tenant do cliente ao **preço público de tabela**.
- Revende ao cliente com a margem que achar adequado — sem interferência da Cadencia no preço final.
- Não há desconto abaixo de R$ 2,50/crédito (piso da tabela, a partir de R$ 1.000 carregados).
- Exceção bulk (> R$ 5.000 em créditos pré-comprados em lote único): negociar caso a caso com Felipe, apenas quando a base justificar (25+ clientes ativos).

**Tabela de preços pública (referência):**

| Valor carregado | Preço/crédito |
|---|---|
| R$ 50 | R$ 7,00 |
| R$ 100 | ~R$ 6,54 |
| R$ 300 | ~R$ 4,94 |
| R$ 500 | ~R$ 3,75 |
| R$ 750 | ~R$ 2,81 |
| R$ 1.000+ | R$ 2,50 (piso) |

> Fonte única de preço: `cadencia-app/src/lib/pricing.ts`. A tabela acima é referência; sempre consultar o sistema antes de citar para o cliente.

---

### Modelo B — Comissão em projeto de implementação

**Quando usar:** o cliente precisa de implementação completa — onboarding, setup de conteúdo, cadências, CRM, agente Lara, domínio. Projeto com setup + mensalidade recorrente.

**Critério de projeto complexo:**

- Envolve setup pago (não é só carga de créditos)
- Tem mensalidade recorrente de gestão ou operação
- Felipe executa o projeto integralmente

**Fluxo:**

1. Revendedor identifica o lead e apresenta o Cadencia.
2. Revendedor agenda reunião — **Felipe faz a call, fecha a venda e assina o contrato com o cliente.**
3. Felipe executa toda a implementação.
4. Revendedor recebe comissão conforme régua abaixo.

**Comissão: 20% sobre setup + mensalidades durante a vigência do contrato.**

---

## Como o revendedor ganha dinheiro

### Modelo A — Margem sobre créditos

O revendedor define o próprio preço ao cliente final. Exemplo prático:

| O revendedor compra | O cliente paga ao revendedor | Margem bruta |
|---|---|---|
| 1.000 créditos × R$ 2,50 = **R$ 2.500** | 1.000 créditos × R$ 4,00 = **R$ 4.000** | **R$ 1.500 (60%)** |
| 1.000 créditos × R$ 2,50 = **R$ 2.500** | 1.000 créditos × R$ 3,50 = **R$ 3.500** | **R$ 1.000 (40%)** |

A margem é inteiramente do revendedor — sem divisão com a Cadencia. Quanto mais clientes, mais recorrente a receita.

### Modelo B — Comissão 20% sobre contrato

```
Comissão = valor da parcela paga pelo cliente × 20%
```

**Incide sobre:** setup (mesmo que parcelado) + mensalidades durante o contrato (padrão 6 meses).

**Prazo de pagamento:** 5 dias úteis após confirmação do pagamento pelo cliente. Nunca antecipado — protege contra inadimplência.

#### Exemplo numérico (projeto médio)

| Item | Valor para o cliente | Comissão do revendedor (20%) |
|---|---|---|
| Setup | R$ 5.990 | R$ 1.198 |
| Mensalidade × 6 meses (R$ 5.000/mês) | R$ 30.000 | R$ 6.000 |
| **Total contrato 6 meses** | **R$ 35.990** | **R$ 7.198** |

> Pagamento parcelado conforme o cliente paga — não em lump sum.

#### Exemplo com 3 clientes ativos (Modelo B)

| Situação | Valor mensal de comissão |
|---|---|
| 3 clientes × R$ 5.000/mês × 20% | **R$ 3.000/mês** |
| 5 clientes × R$ 5.000/mês × 20% | **R$ 5.000/mês** |
| 10 clientes × R$ 5.000/mês × 20% | **R$ 10.000/mês** |

---

## O que a Cadencia faz pelo revendedor

- Suporte técnico ao cliente final (responsabilidade da Cadencia, não do revendedor)
- Treinamento do cliente final (responsabilidade da Cadencia)
- Execução completa dos projetos de implementação (Modelo B)
- Qualificação do lead antes da reunião (Felipe avalia se o lead é ICP)

## O que NÃO está incluído

- Desconto progressivo por volume de indicações: não existe
- Exclusividade geográfica ou de nicho: não garantida
- Antecipação de comissão: nunca antes do pagamento do cliente

---

## Formalização

**Modelo A (créditos):** operacional sem contrato formal — uso direto da plataforma.

**Modelo B (projetos):** comissão registrada por e-mail ou mensagem confirmando o lead indicado + valor do contrato assinado com o cliente. Sem contrato de parceria formal até a base crescer.

---

## Revendedores ativos

| Revendedor | Desde | Modelo | Observações |
|---|---|---|---|
| Vayne Saccaro | 2026-07-21 | A + B | Aluno NoCode Startup; onboarding em andamento |

---

## Refs

- [Processo de Vendas para Revendedores](processo-vendas.md) — como o revendedor apresenta, prospecta e fecha
- [Kit do Revendedor](kit-revendedor.md) — materiais, deck, scripts, objeções
- [Programa de Indicação](../programa-indicacao.md) — programa de indicação CS (diferente de revenda)
- [ICP — Comercial](../icp.md) — perfil do cliente ideal que o revendedor deve mirar
- [Posicionamento](../posicionamento.md) — frases canônicas do produto
