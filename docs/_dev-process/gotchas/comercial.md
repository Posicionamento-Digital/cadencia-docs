---
type: source
source_kind: gotcha
date: 
entities: ["[[Cadencia]]", "[[comercial]]", "[[financeiro]]"]
tags: [gotcha, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Gotchas — comercial

# Gotchas — times/comercial

> Armadilhas técnicas/operacionais validadas (manual review).
> Source: promoção de `gotchas-pending.md` (auto-detect) ou registro manual após sessão de análise.

---

## G001 — Objeção de caixa não se resolve com desconto ou parcelamento

**Validado em:** 2026-05-27 (sessão de análise pós-call Thiago Urréa / Fineven)
**Squad:** geracao-de-negocios (Roberto)
**Tags:** `qualificacao` `bant` `objecao` `proposta`

### Sintoma

Cliente recusa proposta na Hora de Vender (parte 7). Você oferece desconto, escopo reduzido, pagamento parcelado, "paga em 30d depois da entrega" — e **continua recusando**.

Frases-gatilho do cliente:
- *"Hoje eu nem posso, na verdade."*
- *"Prefiro fechar resolvido. Eu gosto de projetar coisa real."*
- *"Eu mesmo não pago isso aí."*
- *"Esse mês eu tive que colocar grana do bolso pra segurar pessoal."*

### Causa real

A objeção **não é preço, escopo ou prazo de pagamento**. É **caixa real apertado** + **aversão a projetar dívida futura** quando o cliente é o próprio CFO/financeiro da empresa.

Quando o decisor é o dono que controla o caixa diretamente, ele não diferencia "fluxo futuro" de "dinheiro agora". Toda promessa futura vira passivo mental. Desconto não muda isso.

### Por que desconto piora (tese do Ultimato)

Aplicando a leitura do jogo do ultimato (Greene, *Tribos Morais*): toda proposta é um ultimato. O respondedor (cliente) aceita ou rejeita conforme **a régua dele de justiça** — não conforme a régua do proponente (Felipe).

Quando o respondedor rejeita, ele está dizendo: *"sua oferta caiu fora da minha régua de justiça — prefiro pagar o custo de não ter o serviço a aceitar essa divisão"*.

Baixar preço dentro do mesmo escopo CONFIRMA pro respondedor que a régua original estava acima da dele. Ele lê o desconto como *"ele estava me cobrando demais antes"*. Em vez de salvar o deal, o desconto **confirma o rejeite** e queima credibilidade.

**Solução:** não mudar a régua dentro do mesmo ultimato. **Mudar o jogo** — escopo menor, modalidade diferente, fase 1 isolada, parceria sem desembolso. Outra oferta, dentro de outra régua possível.

> Referência: léxico em `foundation/leitura-de-sinais.md`. Template em `foundation/template-aposta-de-oferta.md`. Tese aplicada também na etapa 0 da skill `/william`.

### Fix preventivo

1. **Identificar perfil financeiro no BANT da call 1** (qualificação), não na call 2 (proposta). Perguntas:
   - *"Como tá o caixa nos próximos 90 dias?"*
   - *"Quem decide investimentos novos — você sozinho, sócio, conselho?"*
   - *"Tem algum aporte ou rodada de capital prevista pra esse período?"*
2. **Se cliente é também o financeiro:** validar faixa de investimento **antes** de propor. Pergunta:
   - *"Pra um projeto que entrega X em Y dias, qual faixa cabe hoje na Fineven?"*
3. **Se caixa tá apertado:** NÃO propor venda no momento. Opções:
   - Mover pra pipeline Nutrição com trigger temporal (60-90d)
   - Oferecer **parceria de indicação** (sem desembolso) — cliente vira parceiro
   - Oferecer **piloto 100% gratuito** com critério de saída claro (PD assume risco de tempo)
4. **Nunca tentar 3 reframings de preço seguidos na mesma call** — depois de 2 "não", parar e re-qualificar momento.

### Pattern correto

Antes de gastar 15min apresentando proposta de R$ N:

```
[Qualificação 30s no início da call 2]
"Thiago, antes de eu te mostrar — desde a última vez, mudou alguma coisa
do lado de vocês? Caixa, time, prioridade comercial?"
```

Captura mudança de contexto entre call 1 e call 2. Adapta proposta na hora se cenário mudou.

### Caso de origem

Reunião presencial 27/05/2026 com Thiago Urréa (Fineven). Apresentação de proposta R$ 15.000 (pacote completo) + reframing R$ 2.000 (módulo 6 isolado) + concessão de pagamento em 30d. **Todos recusados** — não por preço, mas porque Thiago tinha colocado grana do bolso em maio pra segurar pessoal e é avesso a projetar dívida.

**Sinais que foram revelados tarde demais** (só apareceram no minuto 32 da call de 41min):
- Sócio Renato novo
- Funcionária voltando em junho
- 2 mentorias em curso consumindo recursos
- Maio com aporte pessoal

**Qualquer um desses sinais era pergunta de BANT pré-call.** Detectar em junho/julho na qualificação inicial teria evitado o ciclo inteiro de proposta-recusa-recalibração.

### Referências

- Issue Linear: PDL-299 (retomada 30/06/2026)
- Ata: `Obsidian_Vaults_Empresa/Reuniões/Comercial/2026-05-27 Apresentação Proposta Thiago Urrea Ata.md`
- Sessão de análise: pós-call 27/05/2026

---

## G002 — API GHL opportunities: campo `name`, não `title`

> **[Histórico GHL — superado pela migração ao CRM Cadencia 2026-06-21]** Oportunidades agora vivem no CRM Cadencia (`/api/app/contacts/[id]/opportunities` + trigger `auto_create_opportunity`), não na API GHL. Mantido como registro. Mapa: `_core/GHL-TO-CADENCIA-MIGRATION.md`.

**Validado em:** 2026-05-29 (sessão cadastro leads Geração de Demanda)
**Squad:** geracao-de-demanda (Mafê)
**Tags:** `ghl` `api` `oportunidade`

### Sintoma

POST `/opportunities/` retorna 422 `"property title should not exist"` ao tentar criar oportunidade com o campo `title`.

### Causa real

A API GHL v2021-07-28 de oportunidades usa o campo `name` (não `title`) como nome da oportunidade. A documentação informal e exemplos na web frequentemente mostram `title`, mas o endpoint rejeita.

### Fix

```json
POST /opportunities/
{
  "name": "Lead — Empresa",
  "pipelineId": "...",
  "pipelineStageId": "...",
  "contactId": "...",
  "status": "open",
  "locationId": "..."
}
```

---

## G003 — API GHL calendários: `daysOfTheWeek` exige um objeto por dia

> **[Histórico GHL — superado pela migração ao CRM Cadencia 2026-06-21]** Calendário/agendamento migra para Composio (Google Calendar) — ⏳ a construir (CAD-583/584/585/586). API de calendário GHL não é mais usada. Mantido como registro. Mapa: `_core/GHL-TO-CADENCIA-MIGRATION.md`.

**Validado em:** 2026-05-29 (sessão cadastro leads — configuração openHours calendário)
**Squad:** times/comercial (transversal GHL)
**Tags:** `ghl` `api` `calendario`

### Sintoma

PUT `/calendars/{id}` com `openHours: [{"daysOfTheWeek": [1,2,3,4,5], "hours": [...]}]` retorna 422 `"must be a valid day of week"`.

### Causa real

O endpoint rejeita múltiplos dias num único objeto. Cada dia precisa ser seu próprio objeto no array, com `daysOfTheWeek` contendo apenas um elemento inteiro (0=Dom, 1=Seg, ..., 6=Sáb).

### Fix

```json
"openHours": [
  {"daysOfTheWeek": [1], "hours": [{"openHour": 8, "openMinute": 0, "closeHour": 19, "closeMinute": 0}]},
  {"daysOfTheWeek": [2], "hours": [{"openHour": 8, "openMinute": 0, "closeHour": 19, "closeMinute": 0}]},
  ...
]
```

---

## G004 — API GHL calendários: slots bloqueados quando `openHours: {}`

> **[Histórico GHL — superado pela migração ao CRM Cadencia 2026-06-21]** Agendamento migra para Composio (Google Calendar) — ⏳ a construir (CAD-583/584/585/586). API de calendário GHL não é mais usada. Mantido como registro. Mapa: `_core/GHL-TO-CADENCIA-MIGRATION.md`.

**Validado em:** 2026-05-29 (sessão cadastro leads)
**Squad:** times/comercial (transversal GHL)
**Tags:** `ghl` `api` `calendario` `agendamento`

### Sintoma

POST `/calendars/events/appointments` retorna 400 `"The slot you have selected is no longer available."` mesmo que o horário esteja no futuro e nenhuma outra reunião exista.

### Causa real

Calendário do tipo `event` com `openHours: {}` (vazio) não tem nenhuma disponibilidade configurada — todos os slots são considerados indisponíveis. O erro de "slot não disponível" não é sobre conflito de horário, é sobre ausência de janela de disponibilidade.

### Fix

Configurar openHours antes de criar agendamentos (ver G003). Depois verificar slots reais via:

```
GET /calendars/{id}/free-slots?startDate=<ms>&endDate=<ms>&timezone=America/Sao_Paulo
```
