---
title: Playbook de Retenção
tags: [cs, canon]
---

# Playbook de Retenção — Sinais de Churn e Ações Preventivas

> **Nota (2026-07-17):** Trilha **Franquia / Cadencia Gestores de IA / PD Gestores de IA** descontinuada em 2026-07. As menções abaixo ficam preservadas para referência histórica; ofertas ativas hoje são **PD Consultorias** e **Cadencia SaaS**.


> Doc constitutivo. Identificação proativa de risco de churn + ações por sinal. Proposta-baseline 2026-05-25 — dados históricos da Cadencia ainda precisam ser consolidados pra refinar.

---

## Princípio fundador

**Retenção é preventiva, não reativa.** Quando cliente verbaliza "vou cancelar", já se perdeu 80% da janela de ação. O playbook age em sinais — mesmo sutis — antes da verbalização.

Métrica-chave: **NPS ≥ 8** + **Saúde da Carteira > 85% Pos/Neu** (KPI 4 do CS).

---

## Categorias de sinais

### A) Sinais de Churn Silencioso

Cliente não verbaliza intenção de cancelar, mas comportamento sinaliza.

| Sinal | Força preditiva | Detecção |
|---|---|---|
| 3 dias seguidos Sentimento Negativo na planilha CS | 🔴 Alta | Cron worker (PDL-266 #1 NPS) ou planilha CS |
| Nenhum chamado há >30 dias | 🔴 Alta | Cron worker (PDL-266 #2 sem-contato) |
| Nota Tally pré-encontro <7 sem chamado posterior | 🔴 Alta | Cron worker (PDL-266 #1 NPS) |
| Silêncio após problema reportado (>48h) | 🟡 Média | Manual (planilha CS coluna Status da Resposta = Vácuo) |
| Queda de uso (dependendo do produto — logins, mensagens enviadas pela IA, leads recebidos) | 🟡 Média | ⚠️ Falta instrumentação |
| Mudança de owner interno do cliente | 🟡 Média | Manual (avisar quando cliente menciona nova pessoa) |
| Atraso de pagamento sem aviso | 🔴 Alta | Asaas — webhook ou cron |
| Redução de frequência de reuniões (cliente pedindo "vamos pular essa semana" recorrente) | 🟡 Média | Manual |
| Não preencheu form pré-encontro 2 semanas seguidas | 🟡 Média | Planilha CS (KPI 3 Adesão) |

### B) Sinais de Churn Verbalizado

Cliente expressa diretamente.

| Sinal | Resposta padrão |
|---|---|
| "Vamos rever escopo" | Reunião de re-alinhamento — Felipe + cliente, sem CS, foco em re-fechar contrato |
| "Questiono ROI" | Apresentar dados — relatório de implementação até aqui + KPIs do cliente (não da Cadencia) |
| "Conversei com [concorrente]" | Reunião emergencial Felipe — entender real motivo (preço? feature? relacionamento?) |
| "Atraso/cancelamento de pagamento" | Felipe direto — não delegar pra CS |
| "Não quero mais reunião semanal" | Sinal RUIM — investigar antes de aceitar reduzir |

---

## Ações Preventivas por Sinal

### Sinal 🔴 Alta — Ação CS dentro de 24h
1. Letícia (Felipe operando) **liga** pro cliente (NÃO WhatsApp — telefone)
2. Ouvir sem defender (Chris Voss tactical empathy)
3. Anotar TUDO em ata
4. Criar tarefas concretas no Hub com prazo curto
5. Dar previsão de solução
6. Follow-up em 48h confirmando ação executada

### Sinal 🟡 Média — Ação CS dentro de 3 dias
1. Mensagem proativa contextual ("vi que faltou X — está tudo bem?")
2. Se não responder, ligar
3. Se identificar gargalo, escalar pra Felipe ou Luiz conforme caso
4. Marcar pra acompanhar próximas 2 semanas

### Quando envolver Felipe (escalation)
- Sinal Verbalizado de qualquer tipo
- Sinal Silencioso 🔴 que CS não conseguiu resolver em 48h
- Cliente high-ticket (Consultoria R$10k+/mês, GCI GO) — Felipe entra desde o sinal
- Atraso de pagamento (sempre Felipe)

### Quando envolver Comercial (Eduardo)
- Cliente cancelando pode virar **indicação** se bem encerrado — Eduardo entra na conversa final pra apresentar Programa de Indicação
- Cliente cancelando consultoria pode virar Cadência self-serve — Eduardo apresenta downgrade ao invés de churn total

---

## Critério de "deixar ir"

Aceitar o churn é melhor que segurar em alguns casos. **Não tentar segurar quando:**

1. Cliente está **fora do ICP** (`times/marketing/foundation/icp.md` — ICP não-funciona pra quem quer "solução que roda sozinha sem interação")
2. Cliente já não atende perfil financeiro (mudou contexto — empresa diminuiu, sócio saiu)
3. Custo de retenção > LTV restante (ex: cliente atrasou pagamento 2x já)
4. Cliente "tóxico" — desrespeita time, exige fora de escopo sem aceitar reajuste, abusa de SLA
5. Felipe identifica que cliente vai virar **dor de cabeça operacional** crônica

Quando deixar ir: encerrar **sem queimar ponte**. Cliente bem encerrado pode indicar. Cliente mal encerrado vira detrator.

---

## Dados históricos da Cadencia (lacuna a preencher)

⚠️ **EM ABERTO — Felipe consolidar.**

Análise pendente:
- Quais clientes cancelaram últimos 12 meses?
- Por categoria de produto (Consultoria, Cadencia SaaS, Franquia)?
- Por motivo (verbalizado vs inferido)?
- Quais sinais precoces apareceram?
- Quanto tempo entre primeiro sinal e churn efetivo?
- Quais foram salvos com intervenção? Como?

**Fonte:** CRM Cadencia (oportunidades perdidas no pipeline `geracao-negocios` + churn no pipeline `ciclo-vida`) + memory + conversa com ex-clientes da Cadencia se aceitarem dar retrospecto.

Issue Linear pra ação: PDL-268.

---

## Métricas de retenção

- **NPS médio mensal** — meta ≥ 8
- **% Saúde Carteira Pos/Neu** — meta > 85% (KPI 4)
- **Taxa de churn mensal** — % clientes ativos que cancelaram no mês. Meta a definir (depende do segmento, normal SaaS: <5%/mês)
- **Tempo médio entre sinal e churn** — quanto maior, mais janela de ação
- **Taxa de salvamento** — % clientes em sinal vermelho que foram retidos com intervenção

---

## Refs

- `rotina-cs.md` KPI 4 Saúde da Carteira + seção "Risco de Churn Silencioso"
- `rotina-cs.md` planilha CS (coluna Sentimento + Iniciativa)
- `politica-expansao.md` — relação retenção ↔ expansão (cliente retido bem é candidato expansão)
- `times/marketing/foundation/icp.md` — critérios "não é nosso cliente" (deixar ir)
- `times/comercial/foundation/programa-indicacao.md` — cliente cancelando bem-encerrado pode indicar
- Ciclo de Vida do Cliente — modelado no CRM Cadencia (pipeline `ciclo-vida`); dados históricos a consolidar quando Felipe revisar. (Notion descontinuado — antiga página `2a1a96f9516a81f1825bfa24e1f440f9` fica só como rastro histórico.)
