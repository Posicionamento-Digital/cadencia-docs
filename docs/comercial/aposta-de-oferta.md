---
title: Aposta de Oferta
tags: [comercial, canon]
---

# Template Aposta de Oferta — pré-call

> Template operacional. Preencher antes de toda call de descoberta ou apresentação de proposta.
> Tempo: 3–5 minutos. Local: nota no contato no CRM Cadencia (`/api/app/contacts/[id]/notes`).

---

## Para que serve

Força hipótese explícita sobre **qual é a régua do respondedor** antes da call — e qual estrutura de oferta cabe dentro dela. Sem essa hipótese declarada, o proponente entra na call apostando no escuro e, quando dá errado, ninguém sabe por quê.

A aposta NÃO precisa estar certa. Precisa estar **declarada**. Depois do deal (fechado, perdido ou stall), comparar aposta vs realidade alimenta o léxico em `leitura-de-sinais.md`.

---

## Vocabulário usado

| Termo | Quem |
|---|---|
| **Proponente** | Nós. Felipe. |
| **Respondedor** | O cliente. |
| **Régua** | Padrão pessoal do respondedor sobre o que é "divisão justa de valor". Lida via sinais, não declarada. |

Definições completas em `foundation/leitura-de-sinais.md`.

---

## Template (literalmente o que vai na nota do contato no CRM Cadencia)

```
APOSTA DE OFERTA — [Nome do contato] — [Data]

SINAIS LIDOS:
- [sinal 1 da 1ª mensagem dele]
- [sinal 2 do canal de origem]
- [sinal 3 do perfil/contexto]
- [sinal 4 da conversa até agora]
- [sinal 5 — se houver]

LEITURA DA RÉGUA:
[1 linha descrevendo a régua provável do respondedor — não classificar
em caixinha, descrever]
Exemplo: "régua transacional preço-driven, paciência baixa pra
diagnóstico, espera valor padrão de mercado"

APOSTA DE OFERTA:
- Estrutura: [proposta cheia / fase 1 isolada / Cadência Opção A /
            piloto / parceria sem desembolso]
- Faixa: [R$ X à vista / 12x R$ Y]
- O que INCLUIR: [entregáveis principais + bônus contextuais]
- O que NÃO incluir: [explícito — por exemplo, "sem extras gratuitos
                     porque sinal de paranoia"]

RISCO DE INJUSTIÇA:
[baixo / médio / alto] — [qual sinal me preocupa]
Exemplo: "alto — ele cita NoCode Startup como referência (R$X), nossa
proposta está 2x acima, risco de leitura 'caro demais sem justificativa'"

PLANO B SE REJEITAR:
- [opção 1: escopo menor]
- [opção 2: modalidade diferente]
- [opção 3: parceria sem desembolso]
Nunca: "mesmo escopo com desconto" (G001)
```

---

## Onde puxar os sinais (fontes operacionais)

| Fonte | O que tirar dela |
|---|---|
| **1ª mensagem do contato no CRM Cadencia** | Comprimento, tom, primeira pergunta, vocabulário usado |
| **Canal de origem (UTM, source)** | Indicação direta? Tráfego pago? Live? NoCode Startup? Conteúdo orgânico? |
| **Histórico de interações no CRM Cadencia** (timeline/activities) | Quantas mensagens trocadas? Velocidade de resposta? Sumiu e voltou? |
| **DataStone B2B (enriquecimento)** | Porte, faturamento, sócios, segmento — pistas, não definição |
| **CNPJ.ws (gratuito)** | Razão social, CNAE, situação cadastral |
| **Perplexity Sonar** | Redes sociais, posicionamento público, conteúdo que produz |
| **LinkedIn do decisor** | Cargo, tempo de empresa, formação, conteúdo que compartilha |
| **CEP** | Pista de contexto regional (não classificação, só uma variável a mais) |
| **Pesquisa Google da empresa** | Sinais de busca por preço? Compara orçamentos publicamente? |

> **Nenhuma fonte sozinha define a régua.** Régua é leitura agregada de sinais que se cruzam.

---

## Quality check antes de enviar a oferta

- [ ] Identifiquei pelo menos 3 sinais concretos do respondedor?
- [ ] A leitura da régua descreve, não classifica?
- [ ] A faixa da proposta cabe dentro da régua identificada?
- [ ] Se a leitura é "régua paranoica", removi todos os extras gratuitos?
- [ ] Se a leitura é "régua machiguenga / quer começar pequeno", reduzi escopo em vez de descontar?
- [ ] Tenho plano B declarado caso o respondedor rejeite?
- [ ] O plano B é "mudar o jogo" (escopo/modalidade), não "baixar preço"?

---

## Exemplo preenchido — Eliseu Rocha (08/06/2026, retroativo)

```
APOSTA DE OFERTA — Eliseu Rocha — 08/06/2026

SINAIS LIDOS:
- consultor IA com clientes ativos (case Sentry + Telegram concreto)
- assistiu live antes da call (régua puxada pelo conteúdo)
- "estou fazendo na unha" (gargalo concreto)
- cita NoCode Startup como referência de curso
- detalha síndrome do impostor e dificuldade de se posicionar
  (sinal emocional alto)

LEITURA DA RÉGUA:
"régua valor-driven com camada emocional pesada — vai responder a
demonstração concreta + visão de futuro de 30 dias. NoCode Startup
é a âncora de preço (precisa diferenciar)"

APOSTA DE OFERTA:
- Estrutura: treinamento + acompanhamento 30 dias
- Faixa: R$5.000 à vista / 12x R$500 (total R$6.000)
- INCLUIR: bônus contextuais emergidos da call (Cadência 30 dias,
  posicionamento de marca, escopo de vendas) — não pré-definidos
- NÃO incluir: comparação direta com NoCode (diferenciar via
  "ensino o porquê de cada decisão")

RISCO DE INJUSTIÇA:
médio — preço 2x acima do NoCode Startup, precisa quebrar comparação
e fazer demo ao vivo antes do preço

PLANO B SE REJEITAR:
- Cadência Opção A (R$399/mês) como porta de entrada
- Parceria de indicação (sem desembolso)
- Não usar: desconto no mesmo escopo
```

---

## Refs

- `foundation/leitura-de-sinais.md` — léxico completo de sinais
- `foundation/learnings-calls-vendas.md` — loop de feedback pós-deal
- `gotchas.md` G001 — por que desconto confirma rejeite
- `skills/william.md` etapa 0 — releitura quando rejeitam a aposta
