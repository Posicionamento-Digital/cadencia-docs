---
title: Rituais Solo
tags: [comercial, canon]
---

# Rituais de Gestão — Operação Solo + Automação

> Adaptação dos rituais Cauduro (Daily/Weekly/One-on-One/Roleplay/Chat Review/Call Review) para operação solo com Sistema Comercial PD.
> Princípio base: **rituais self-management** via Stamper. Felipe não tem 1:1 com SDR humano — tem 1:1 consigo mesmo via Stamper e dados.
> Consolidado 2026-05-25.

---

## Mapa dos rituais

| Ritual | Frequência | Duração | Owner | Status |
|---|---|---|---|---|
| **Daily com Stamper** | Diária 9h | 15-30min | Stamper | ✅ Existe (`/abrir-dia`) |
| **Weekly Comercial** | Sexta 17h | 30min | Eduardo + Felipe | ⏳ Implementar |
| **Forecast Mensal** | Última 6ª do mês | 1h | Eduardo + Felipe | ⏳ Implementar |
| **Pipeline Review** | Quarta 10h | 15min | Felipe via CRM Cadencia | ⏳ Implementar |
| **Call Review com IA** | Após cada call gravada | 10min | Sistema Comercial PD (futuro) | ❌ Gap roadmap |
| **Chat Review automático** | Diário (background) | n/a | Sistema Comercial PD (futuro) | ❌ Gap roadmap |

---

## 1. Daily com Stamper (existe, integra Comercial)

**Quando:** Toda manhã, ao Felipe abrir o dia (`/abrir-dia` ou similar).

**Stamper já faz:**
- Puxa issues Linear atribuídas a Felipe
- Lê Daily Note Obsidian (tarefas pessoais)
- Monta plano em blocos de tempo
- Cria eventos Google Calendar

**Integração Comercial a adicionar:**
- Stamper consulta os pipelines do Squad no CRM Cadencia (via Sistema Comercial PD quando pronto)
- Identifica leads em "Tentando Contato" que precisam de touchpoint no dia
- Identifica leads em "Em conversa" sem follow-up há >24h
- Identifica propostas em "Negociação/Follow-up" prontas pra ligação D+3
- Sugere prioridades do dia comercial

**Output esperado:**
```
== Comercial hoje ==
- 12 leads em cadência (3 no Dia 1, 4 no Dia 5, 5 no Dia 9)
- 2 propostas em FUP (Mlau Fernandes D+3, WGL D+1)
- 1 reunião agendada às 14h (Sandro)
== Priorize: ==
1. Mafê executa cadência diária (Sistema rodando)
2. Você: FUP Mlau Fernandes 10h30
3. Reunião Sandro 14h
4. Roberto: preparar próxima proposta
```

---

## 2. Weekly Comercial (a implementar)

**Quando:** Sexta-feira 17h (último bloco da semana, antes do encerramento 17:30).

**Duração:** 30min (não pode estourar).

**Estrutura:**
1. **Métricas da semana** (5min)
   - Leads novos enriquecidos
   - Conversas iniciadas
   - Reuniões agendadas (MQL)
   - Reuniões realizadas (SQL)
   - Propostas enviadas
   - Vendas fechadas
2. **Análise vs meta** (5min)
   - Pipeline está saudável?
   - Tem gargalo em algum stage?
   - Algum lead Hot esquecido?
3. **Aprendizados** (10min)
   - Quais scripts/cadências performaram?
   - Quais objeções novas apareceram?
   - Algum padrão de no-show ou desqualificação?
4. **Ajustes próxima semana** (10min)
   - Mudar mensagem da cadência?
   - Priorizar trilha?
   - Refazer abordagem em algum lead específico?

**Output:** entrada em `memory/STATE.md` (atualiza L1 + L2) + entrada em `decisions.md` se mudou estratégia.

**Quem conduz:** Eduardo (persona) facilita, Felipe executa.

---

## 3. Forecast Mensal (a implementar)

**Quando:** Última sexta-feira do mês.

**Duração:** 1h.

**Estrutura:**
1. **Recap do mês** (15min)
   - Resultado vs meta (leads, conversas, reuniões, vendas, R$)
   - Custo de aquisição (R$ enriquecimento + tempo Felipe)
   - Comparação com mês anterior
2. **Forecast próximo mês** (15min)
   - Pipeline atual quanto pode fechar?
   - Leads novos esperados (base atual × cadência 10D)
   - Sazonalidade?
3. **Decisões estratégicas** (20min)
   - Trilha alvo do mês (Consultorias vs Gestores IA)
   - Ajustes no Sistema Comercial PD
   - Novos parceiros de indicação a ativar
4. **Compromissos do mês** (10min)
   - 3-5 metas concretas e mensuráveis
   - Riscos identificados

**Output:** doc mensal em `memory/forecast/YYYY-MM.md` (a criar pasta quando for ter histórico) + entradas em `decisions.md`.

---

## 4. Pipeline Review (a implementar)

**Quando:** Quarta-feira 10h.

**Duração:** 15min (revisão rápida).

**O que fazer:**
- Abrir o CRM Cadencia (ou dashboard do Sistema Comercial PD quando pronto)
- Verificar leads em "Stand-by" há mais de 14 dias (decidir: nutrir, reativar ou descartar)
- Verificar leads em "Em conversa" sem movimentação há >5 dias (cobrar resposta ou avançar)
- Verificar propostas em "Negociação" há >10 dias sem fechamento (rever estratégia)
- Verificar leads "Hot" recebidos do Marketing (não esquecer)

**Output:** ações imediatas (movimentação manual ou comando para Sistema Comercial PD).

---

## 5. Call Review com IA (gap — roadmap)

**Visão:** após cada call de vendas (gravada via Fireflies ou similar), IA escuta + cruza com:
- Framework REP-G (avaliar adesão aos G3-G5)
- Framework Call de Vendas Challenger (7 partes — Aquecimento → Reestruturação → Angústia → Impacto → Novo Caminho → Solução → Fechamento)
- `playbook-objecoes.md` (objeções quebradas / não quebradas)

**Output:** feedback estruturado em <10min após a call.

**Status:** ❌ não existe. Issue Linear a criar.

---

## 6. Chat Review automático (gap — roadmap)

**Visão:** Sistema Comercial PD analisa em background as conversas WhatsApp/Email do funil ativo + cruza com:
- `cadencia-10d.md` (executando os 7 touchpoints conforme planejado?)
- `rep-g.md` (mensagens respeitam progressão G1→G5?)
- `principios-cauduro.md` ("criança de 8 anos"? canais triangulando?)

**Output:** alertas semanais para Felipe se algum padrão estiver fora do playbook.

**Status:** ❌ não existe. Issue Linear a criar.

---

## Princípio operacional

**Cauduro:** _"O vendedor não tem passado. Todo mês a gente tem que performar, todo mês a gente tem que ir atrás da meta."_

Adaptado solo: **Felipe não tem mês passado.** Forecast mensal força olhar pra frente. Pipeline review semanal força olhar agora. Daily diário força executar hoje.

---

## Implementação

**Fase 1 (imediato):** Daily com Stamper + Pipeline Review manual (quarta 10h)
**Fase 2 (com Sistema Comercial PD básico):** Weekly Comercial estruturado + Forecast mensal
**Fase 3 (futuro):** Call Review IA + Chat Review automático

Cada implementação gera issue Linear no projeto Comercial.

---

## Refs

- `principios-cauduro.md` — princípios que sustentam esses rituais
- `../context/stack-tecnico.md` — Sistema Comercial PD habilitará rituais 5 e 6
- `stamper/skills/abrir-dia/` — base do ritual Daily
- Estudo Cauduro: `C:\Users\felip\Obsidian_Vaults_Pessoal\Estudo\Vendas\2026-05-25_como-montar-time-vendas-fatura-milhoes.md`
