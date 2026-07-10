---
date: 2026-05-14
tags: [skill, infra, ecuro, ghl, funil, cac, ltv, ia, tecnologia, automacao]
moc: "[[MOC-Skills]]"
---
# Analise Funil Ecuro

Análise completa de funil de conversão de qualquer clínica com acesso ao eCuro. Puxa dados, cruza com GHL, calcula CAC/LTV, identifica gargalos por tempo de espera e publica relatório no Notion.

## Quando usar
"/analise-funil-ecuro [clínica] [período]", "analisa o funil da Ceilândia", "como tá o funil da Central", "diagnóstico de funil", "relatório de conversão [clínica]".

---

## Conteúdo da Skill

```markdown
---
name: analise-funil-ecuro
description: Análise completa de funil de conversão de qualquer clínica com acesso ao eCuro. Puxa dados, cruza com GHL, calcula CAC/LTV, identifica gargalos por tempo de espera, e publica relatório no Notion.
---

# Análise de Funil eCuro — Skill de Diagnóstico

Puxa dados do eCuro + GHL, analisa funil ponta a ponta, identifica gargalos, calcula métricas financeiras e publica relatório estruturado no Notion.

## Parâmetros

| Parâmetro | Obrigatório | Exemplo |
|---|---|---|
| Clínica | Sim | "Ceilândia", "Central GO" |
| Período | Não (default: último mês completo) | "abril", "março e abril", "últimos 60 dias" |
| Página Notion destino | Não (default: página GCI Regional Goiás) | URL Notion |

## Mapeamento de Clínicas

Buscar IDs em `C:\Users\felip\.openclaw\workspace\src\clients\sorria\`:

| Unidade | clinicId (eCuro) | Config |
|---|---|---|
| Ceilândia (DF) | `f6e9a41d-e7d1-4b8a-9463-859cb00b9df0` | `ceilandia/config.py` |
| Central (GO) | buscar em `central/config.py` → `ECURO_CLINIC_ID` | `central/config.py` |

## Fluxo de Execução

### Fase 1 — Coleta de Dados

1. **Identificar clínica**: mapear nome → clinicId
2. **Identificar canal PD**: ler `config.py` da unidade → `ECURO_PD_CHANNEL` e verificar channelId associado
3. **Puxar agendamentos do eCuro** (semana a semana para não estourar limite):
   ```
   mcp__claude_ai_ecuro__get_appointments_appid(clinicId, dateRange, all=true)
   ```
4. **Puxar dados GHL** (se houver PIT configurado no .env da unidade)
5. **Puxar tratamentos financeiros** dos pacientes PD atendidos:
   ```
   mcp__claude_ai_ecuro__patient_incomplete_treatments(patientId)
   ```

### Fase 2 — Processamento

1. **Identificar canal PD via channelId** — confirmar pelo padrão: 80%+ criado por NULL/API
2. **Limpar duplicados IA**: cancellationReason contém "duplicado" ou "errado"
3. **Separar avaliações vs procedimentos**
4. **Calcular métricas**:
   - Status: 8=atendido, 11=cancelado, 12=no-show
   - Comparecimento por canal (PD vs outros)
   - Comparecimento por criador (Lara/API vs CRC/humano)
   - Tempo de espera (createdAt → scheduledStartTime) em buckets: mesmo dia, 1 dia, 2-3 dias, 4+ dias
   - Comparecimento por dia da semana e horário BRT (UTC-3)
   - Antecedência de cancelamento (antes ou depois do horário)
   - Motivos de cancelamento (top 10)
   - Pacientes únicos novos por semana

5. **Cruzamento GHL** (se disponível):
   - Total leads metaads no período
   - Taxa engajamento
   - Conversas criadas vs agendamentos no eCuro

6. **Financeiro**:
   - Para cada paciente PD atendido em avaliação: buscar patient_incomplete_treatments
   - Separar APPROVED (statusName) vs PLANNED
   - Totalizar: valor total, ticket médio, quantidade

### Fase 3 — Análise (Método Pólya)

**Hipóteses recorrentes a testar:**
- H1: Tempo de espera correlaciona com no-show
- H2: Lara (API) vs CRC (humano) — quem tem melhor taxa?
- H3: Cancelamentos têm antecedência resgatável?
- H4: Horários específicos têm pior taxa?
- H5: Volume crescente degrada taxa?

**Benchmarks internos (baseados em Ceilândia mar/abr 2026):**
- Lead → Agendamento: 20-26%
- Agendamento → Comparecimento canal PD: 21-29%
- Agendamento → Comparecimento outros canais: 50-53%
- Comparecimento → Venda: 90%
- Tempo de espera ideal: < 24h (44-50% comp)

### Fase 4 — Relatório Notion

Publicar subpágina na página da clínica no Notion.

**Formato Notion OBRIGATÓRIO:**
- Tabelas em XML (`<table>`, `<tr>`, `<td>`) — NUNCA markdown pipe tables
- Callouts com `<callout icon="emoji" color="cor_bg">`
- Cores: `red_bg` problemas, `green_bg` positivos, `orange_bg` alertas, `gray_bg` informativo, `blue_bg` insights, `purple_bg` objetivos

**Estrutura do relatório:**
1. Resumo executivo (quote block)
2. O Número que Importa (tabela tempo × comparecimento)
3. Comparativo meses
4. O que os dados revelam (callouts)
5. Funil Ponta a Ponta (ASCII cascade)
6. Onde o dinheiro está sendo perdido (callout red_bg)
7. Causa Raiz
8. CAC e LTV — Atual vs Projetado
9. Projeção de Receita com Intervenções (4 cenários)
10. Plano de Execução — PD
11. Resumo da Proposta
12. Dados Financeiros Confirmados

## Cálculos Padrão

### CAC
```
CAC por paciente na cadeira = Investimento ads / Pacientes atendidos (canal PD)
CAC por venda = Investimento ads / Vendas assinadas (status APPROVED)
```

### LTV
```
LTV inicial = Ticket médio dos tratamentos criados no período
```

## Regras

- NUNCA inventar dados. Se um endpoint falhar, avisar e prosseguir com dados parciais.
- SEMPRE confirmar channelId com múltiplas evidências antes de assumir que é canal PD.
- NUNCA expor nomes completos de pacientes em relatórios — usar primeiro nome apenas.
- Valores financeiros: SEMPRE separar APPROVED (assinado) de PLANNED (planejado).
- Projeções: deixar claro que são estimativas baseadas em dados históricos.
- Se `apireport` falhar (restrição de horário 20h-8h BRT): usar `get_appointments_appid`.
- Se dados GHL não disponíveis: prosseguir só com eCuro e avisar nas limitações.
- Verificar se contatos GHL são reais ou import em batch (todos criados no mesmo dia = suspeito).
- Separar avaliações de procedimentos para não inflar funil de captação.
```

## Notas Relacionadas
[[Infra-GHL-Financeiro/Criar User GHL]] · [[Marketing-Cadencia/Meta Ads]]
