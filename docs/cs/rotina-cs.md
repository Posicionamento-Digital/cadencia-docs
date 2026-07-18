---
title: Rotina CS — Diária, Semanal, Mensal + 5 KPIs
tags: [cs, canon]
---

# Rotina CS — Diária, Semanal e Mensal + 5 KPIs

> Doc constitutivo. Base do dia-a-dia do Squad `relacionamento/` aplicada a TODOS os clientes ativos.
> Fonte: Notion "Playbook - Acompanhamento e Sucesso do Cliente (CS)" (`2fda96f9516a80e88d09d7667ebacd3d`), publicado 04/02/2026 por Felipe. Consolidado pro framework em 2026-05-25.

---

## Objetivo da rotina

Estabelecer rotina **proativa** de Customer Success pra:
- Garantir satisfação do cliente (NPS > 9)
- Aumentar transparência na resolução de problemas
- Otimizar tempo das reuniões semanais
- Identificar oportunidades de upsell

---

## ROTINA DIÁRIA

### Contato Proativo (manhã)
- Enviar mensagem pra cada parceiro: *"Está tudo certo hoje? Precisam de algo no projeto?"*
- Cobrar parceiros que não responderam ao longo do dia

### FUPs
- Retornar clientes com pendência do dia anterior
- Follow-up de clientes com Sentimento Negativo/Crítico do dia anterior
- Verificar status de problemas escalados (Luiz pra técnico; Felipe pra gestão) e atualizar cliente

### Suporte
- Verificar chamados abertos no Hub e dar andamento
- Verificar funcionamento dos produtos de cada cliente (IA, automações, CRM)
- Escalar problemas técnicos pro Luiz
- Escalar problemas de gestão pro Felipe
- Verificar clientes desconectados e notificar

### Relatórios
- Preencher planilha de Acompanhamento Diário (todas colunas, todos clientes)
- Registrar métricas do dia no Obsidian (vault Time PD; Notion descontinuado)
- Extrair, analisar e enviar relatórios de Performance IA (toda segunda)

### Fluxograma — Contato Diário

```
INÍCIO DO DIA (manhã)
       ↓
Mensagem pra cada parceiro
       ↓
Cliente relatou problema?
   ├─ SIM → É urgente?
   │         ├─ SIM → Escalar Felipe
   │         └─ NÃO → Suporte (Luiz)
   └─ NÃO → Registrar ponto de contato positivo
```

---

## ROTINA SEMANAL

### FUPs
- Atualizar status de cada projeto antes dos follow-ups
- Enviar resumo de resultados da semana pra cada parceiro
- Verificar clientes com chamado aberto há mais de 48h sem retorno
- Cobrar Luiz/Felipe sobre escalações pendentes

### Formulários
- Enviar link Tally **48h antes** da reunião (GCI GO + GCI RJ + outros clientes recorrentes)
- Cobrar preenchimento **24h antes** — sem formulário = reunião cancelada
- Skill: `/tally-form-briefing-cs`

### Reuniões Regionais
- Extrair dados de CRM por regional
- Analisar formulários pré-encontro
- Montar relatório comparativo semana anterior
- Realizar Reunião Regional GO
- Realizar Reunião Quinzenal GCI RJ

### Implementações
- Verificar status de clientes em implementação no Kanban
- Atualizar checklist de implementação no Obsidian (vault Time PD; referência: `playbook-implementacao-11-fases.md`)
- Enviar comunicação de alinhamento (status + próximos passos)

### Relatórios / Fechamento
- **Calcular os 5 KPIs da semana** (ver seção KPIs abaixo)
- Listar clientes com Sentimento Negativo/Crítico e ações tomadas
- Preparar respostas pra Reunião de Revisão com gestão (Felipe — Bloco 1: Números, Bloco 2: Clientes em Risco, Bloco 3: Oportunidades)
- Ligar pra cada unidade (fechamento 10-15 min via telefone)

### Fluxograma — Fechamento Semanal

```
Agendar reunião rápida (10-15 min) via TELEFONE com cada unidade
       ↓
PAUTA DA LIGAÇÃO:
  1. Audição de dados (leads e vendas)
  2. Alinhar tarefas pendentes
  3. Verificar automações em aberto
```

### Fluxograma — Ação sobre NPS Baixo

```
Nota < 7 ou feedback crítico negativo?
   ├─ SIM → LIGAR IMEDIATAMENTE
   │         ↓
   │      1. Ouvir dores
   │      2. Anotar tudo
   │      3. Criar tarefas no Hub
   │      4. Dar previsão de solução
   └─ NÃO → Seguir rotina normal
```

---

## ROTINA MENSAL

### Suporte
- Levantar chamados recorrentes (>3x em 30 dias) → reclassificar como **Ponto de Atenção**
- Atualizar Esteira de Projetos com todos os chamados abertos

### Implementações
- Revisar critérios de saída de fase por cliente (Playbook 11 fases)
- Identificar bloqueios e escalar

### Relatórios / Alertas
- Identificar clientes sem chamado há +30 dias e ligar
- Identificar clientes sem chamado há +10 dias e ligar
- Verificar meta NPS ≥ 8 por unidade
- Verificar clientes com renovação em 30 dias

### Comercial
- Consolidar oportunidades de upsell do mês

### Consultorias Mensais
- Agendar consultoria com cada unidade
- Extrair dados CRM: comparativo mês anterior vs atual
- Preparar relatório de performance por unidade
- Preparar apresentação com template padrão
- Realizar consultoria (resultados + estratégia + próximos passos)
- Registrar ata no Obsidian (vault Time PD) com decisões e responsáveis

---

## Planilha Diária de Acompanhamento

> Por que preencher todo dia: é a principal ferramenta de trabalho. Mostra valor entregue, protege de cobranças injustas, identifica problemas antes de virarem crise. Sem dados, não há como provar trabalho nem melhorar.

### Estrutura (colunas)

**Grupo 1: Identificação**
| Coluna | O que preencher |
|---|---|
| Data | Data do contato (ex: 04/02/2026) |
| Nome da Unidade | Selecionar cliente no menu suspenso |

**Grupo 2: Ação do CS**
| Coluna | Opções |
|---|---|
| Canal de Contato | WhatsApp / Telefone / Reunião |
| Iniciativa do Contato | **Proativa** (você chamou) / **Reativa** (cliente chamou) ← campo mais importante |
| Status da Resposta | Respondido / Vácuo / Aguardando |

**Grupo 3: Saúde do Cliente**
| Coluna | Opções |
|---|---|
| Sentimento do Dia | Positivo 😊 / Neutro 😐 / Negativo 😟 / Crítico 🚨 |
| Form Pré-Reunião? | Sim / Não / N/A |

**Grupo 4: Resolução**
| Coluna | Opções |
|---|---|
| Houve Problema? | Sim / Não |
| Tipo de Problema | Técnico (Bug) / IA (Alucinação) / Dúvida / Processo |
| Ação Tomada | Resolvido na hora / Escalado Suporte (Luiz) / Escalado Gestão (Felipe) |

**Grupo 5: Comercial**
| Coluna | Opções |
|---|---|
| Oportunidade Upsell? | Sim (descrever) / Não — comissão 5-20% |

### Classificação Sentimento do Dia

| Sentimento | Sinais | Ação |
|---|---|---|
| **Positivo** 😊 | Cliente elogia, agradece, demonstra satisfação | Registrar, manter relacionamento |
| **Neutro** 😐 | Respostas curtas ("ok", "tudo certo"), sem emoção | Normal, seguir rotina |
| **Negativo** 😟 | Reclamação pontual, frustração, demora em responder | Investigar causa, registrar problema |
| **Crítico** 🚨 | Cliente irritado, ameaça cancelar, múltiplas reclamações | LIGAR IMEDIATAMENTE, escalar |

⚠️ **3 dias seguidos de Negativo = alerta vermelho.** Ligar HOJE, não esperar reclamação formal.

---

## Os 5 KPIs CS

KPIs duros, semanalmente apurados. Resumem o trabalho da semana — a gestão (Felipe) olha esses 5 antes de detalhe.

### KPI 1: Taxa de Proatividade
**Fórmula:** `(Contatos Proativa ÷ Total Contatos) × 100`
**Meta:** > 80%
**Significado:** você está "caçando" problemas ou só apagando incêndios?
**Como melhorar:** mensagem de "bom dia" ANTES do cliente reclamar. Todo dia. Sem exceção.

### KPI 2: Índice de Resposta (Engagement Rate)
**Fórmula:** `(Contatos Respondidos ÷ Total Contatos Tentados) × 100`
**Meta:** > 90%
**Significado:** clientes estão respondendo? Baixo = abordagem errada.
**Como melhorar:** mudar horário das mensagens, mudar tom (mais pessoal), ligar em vez de WhatsApp.

### KPI 3: Adesão ao Processo (Compliance)
**Fórmula:** `(Formulários Entregues no Prazo ÷ Reuniões Realizadas) × 100`
**Meta:** 100%
**Significado:** conseguindo educar clientes a seguir as regras (formulário 24h antes)?
**Como melhorar:** cobrar formulário 48h antes (não 24h); avisar que reunião será cancelada; ser firme — sem formulário = sem pauta = sem reunião.

### KPI 4: Saúde da Carteira (Sentiment Score)
**Cálculo:** % clientes Positivo/Neutro vs % Negativo/Crítico
**Meta:** > 85% Positivo/Neutro
**Alerta automático:** 3 dias seguidos Negativo em um cliente → alerta vermelho. Mesmo sem chamado aberto, esse cliente está em risco. Ligar HOJE.

### KPI 5: Eficiência de Resolução (FCR — First Contact Resolution)
**Fórmula:** `(Problemas "Resolvido na hora" ÷ Total Problemas) × 100`
**Meta:** > 60%
**Significado:** quantos problemas resolve sozinho sem escalar. Quanto mais escala, mais vira "repassador de recados".

### Resumo dos 5 KPIs

| KPI | Meta | Se estiver abaixo |
|---|---|---|
| Taxa de Proatividade | > 80% | Você está só apagando incêndio |
| Índice de Resposta | > 90% | Clientes não veem valor no contato |
| Adesão ao Processo | 100% | Reuniões estão sendo improdutivas |
| Saúde da Carteira | > 85% Pos/Neu | Base instável, risco cancelamentos |
| Eficiência de Resolução | > 60% | Você está só repassando problemas |

---

## Reunião de Revisão Semanal (15 min)

Pauta com gestão (Felipe):

**Bloco 1 — Números (5 min)**
- Qual foi sua Taxa de Proatividade essa semana?
- Quantas unidades não preencheram o formulário? Por quê?

**Bloco 2 — Clientes em Risco (5 min)**
- Quais clientes tiveram Sentimento Negativo/Crítico?
- O que você fez pra reverter?
- Precisa de intervenção da gestão?

**Bloco 3 — Oportunidades (5 min)**
- Marcou Upsell em algum cliente. Já agendou call de vendas?
- Qual foi o principal tipo de problema da semana (Técnico ou IA)?

---

## Precauções e alertas

### Risco de Churn Silencioso
| Sinal de Alerta | Ação Imediata |
|---|---|
| Cliente dá nota baixa mas não abre chamado | Investigar ativamente |
| Nenhum chamado há >30 dias | Ligar pra verificar satisfação |
| Silêncio após problema reportado | Follow-up em 48h |

### Humanização do Atendimento
- **Usar apelidos** ("Nati", "Gabi") pra criar conexão
- **Exceção:** clientes muito formais — manter formalidade

### Separação de Canais (PEDRA ANGULAR)
Ver `separacao-cs-suporte.md`. Resumo: CS resolve insatisfação + cuida do relacionamento. Suporte resolve bug técnico + cuida da ferramenta. **Não misturar canais**.

---

## Critérios de sucesso

- NPS médio das unidades ≥ 8 (meta original era até fevereiro 2026)
- 100% de adesão ao preenchimento do formulário pré-reunião
- Redução de chamados recorrentes (reincidência)

---

## Análise de riscos

| Risco | Contingência |
|---|---|
| Cliente parar de abrir chamados e cancelar silenciosamente | Monitoramento ativo de "último contato" e "último chamado". Alerta se >15 dias sem contato |
| Formulário não preenchido consistentemente | Reunião se torna opcional/cancelada automaticamente |
| Acúmulo de Pontos de Atenção | Reunião de crise com Time Técnico + Diretoria (Felipe) |
