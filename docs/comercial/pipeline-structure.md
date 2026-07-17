---
title: Pipeline Structure
tags: [comercial, canon]
---

# Pipeline Structure — Time Comercial

> Estrutura dos pipelines do **CRM Cadencia** ativos no Squad + critérios entre stages + handoff entre sub-squads.
> A operação comercial roda no **CRM próprio Cadencia**, como tenant do produto (`6bb2c1ba-7fb3-416a-b523-7c9561ea8db3`).
>
> **NOTA:** Pipeline `nutricao` (Frio/Aquecendo/Quente/Hot + scoring) NÃO está detalhado aqui — é responsabilidade de `times/marketing/nutricao/`.

---

## Regras estruturais

1. **Pipeline "Enriquecimento" não existe mais** (removido em CAD-653). As 1.029 oportunidades legadas foram migradas para `geracao-demanda` / `novos-leads`. Enriquecimento agora é **processo de dados** (tabela `lead_enrichments` + rotas `/api/app/enrichment`), não um funil visual.
2. **Slugs canônicos:** `geracao-demanda` e `geracao-negocios` (sem "de"), `nutricao`, `ciclo-vida`.
3. **Stages por slug.** O slug é determinístico no seed; UUIDs ficam no app/Supabase.
4. **Novo pipeline `ciclo-vida` (LTV)** pós-fechamento — ver §4.

---

## Visão geral — funis do Squad

```
[Marketing/nutricao]                    [Comercial — este Squad]
                                        ┌──────────────────────────────────────────────┐
Pipeline `nutricao`                     │                                              │
(Frio/Aquecendo/Quente/Hot)             │  Enriquecimento (processo de dados)          │
        │                               │           │ grava em contacts/lead_enrichments│
   Lead Hot ────handoff────────────────►│   Pipeline `geracao-demanda`                 │
                                        │           │                                  │
                                        │   Lead SQL (Reunião realizada)               │
                                        │           │                                  │
                                        │   Pipeline `geracao-negocios`                │
                                        │           │                                  │
                                        │   Cliente fechado ──handoff──► [CS] + `ciclo-vida` │
                                        └──────────────────────────────────────────────┘
```

---

## Enriquecimento — processo de dados (não é mais funil)

**Squad dono:** `geracao-de-demanda`
**Função:** leads novos passam por cascata de enriquecimento (CNPJ.ws → DataStone B2C → DataStone B2B → Perplexity Sonar) antes de entrar na cadência ativa.
**Onde vive agora:** rotas `/api/app/enrichment`, `enrichment/prospect`, `enrichment/search`, `enrichment/parse-icp` → grava em `public.contacts` + tabela `lead_enrichments`.
**Classificação ICP:** `contacts.is_icp` + `contacts.score`. Lead enriquecido e qualificado entra direto no pipeline `geracao-demanda` no stage `novos-leads`.

### Critério de entrada no funil
- **→ `geracao-demanda`/`novos-leads`:** score ≥ 50 E fontes ≥ 2, OU nome + email + telefone validados.
- **Fora do ICP:** `is_icp = false` — fica fora do funil (revisar manualmente antes de descartar).

---

## Pipeline `geracao-demanda` — "Geração de Demanda"

**Squad dono:** `geracao-de-demanda`
**Função:** Prospecção ativa pela cadência 10D REP-G. Da abordagem inicial até a reunião realizada (SQL).

### Stages

| Stage (slug) | Nome | Descrição | Critério de saída |
|---|---|---|---|
| `novos-leads` | Novos Leads | Enriquecidos prontos pra abordagem (Dia 1 da cadência) | Iniciou cadência → Tentando Contato |
| `triagem` | Triagem | Análise manual antes de iniciar cadência | Pronto pra cadência → Tentando Contato |
| `tentando-contato` | Tentando Contato | Ciclo de cadência ativo (Dias 1-10) | Lead respondeu → Em conversa; OU esgotou cadência → StandBy |
| `em-conversa` | Em conversa | Lead respondeu, em qualificação | Lead qualificado + interessado → Call agendada |
| `call-agendada` | Call agendada | Pré-call agendada com SDR (Mafê) | Confirmou → Call realizada; OU no-show → FUP |
| `call-realizada-qualificacao` | Call realizada (Qualificação) | Pré-call SDR aconteceu | Lead = MQL → Reunião Agendada; OU desqualifica → StandBy |
| `reuniao-agendada-mql` | Reunião Agendada (MQL) | Reunião com Closer (Roberto) agendada | Confirmou 1h antes → Reunião Confirmada |
| `reuniao-confirmada` | Reunião Confirmada | Lead confirmou presença | Reunião aconteceu → SQL → **handoff Geração de Negócios** |
| `standby` | StandBy | Sem resposta após cadência completa | Reativação manual ou expira em 90 dias |

### Handoff para Geração de Negócios
Quando lead vira **SQL** (Reunião Realizada), a oportunidade move para `geracao-negocios`/`reuniao-realizada-sql` + notificação para Roberto. Hoje manual; automação de stage→trigger é **⏳ a construir (CAD-581)**.

---

## Pipeline `geracao-negocios` — "Geração de Negócios"

**Squad dono:** `geracao-de-negocios`
**Função:** Pós-qualificação. Reunião realizada → proposta → negociação → fechamento.

### Stages

| Stage (slug) | Nome | Descrição | Critério de saída |
|---|---|---|---|
| `reuniao-realizada-sql` | Reunião Realizada (SQL) | Closer conduziu reunião, identificou oportunidade real | Proposta preparada → Proposta Enviada; OU desqualifica → StandBy |
| `proposta-enviada` | Proposta Enviada | Proposta enviada formalmente (PDF + WhatsApp + email) | Respondeu → Negociação; OU silêncio → cadência FUP D+1/3/5/7/10 |
| `segunda-reuniao-apresentacao-proposta` | Segunda Reunião (Apresentação Proposta) | Alinhamento ou apresentação detalhada | Avançou → Negociação |
| `negociacao-follow-up` | Negociação/Follow-up | Em discussão de termos, valores, escopo | Aceitou → Fechamento; OU recusou → StandBy |
| `fechamento` | Fechamento (terminal) | Contrato + pagamento processando | Cliente fechado → **handoff CS** + entra em `ciclo-vida` |

> Piloto/PoC é tratado dentro de `negociacao-follow-up`; não existe stage separado "Em teste".

### Handoff para CS
Cliente fechado dispara: (1) notificação CS, (2) briefing de onboarding, (3) handoff de Roberto via call/doc + entrada no pipeline `ciclo-vida`.

---

## Pipeline `ciclo-vida` — "Ciclo de Vida do Cliente" (LTV)

Pós-fechamento, acompanha retenção e expansão (operado junto com CS).
`cliente-novo` → `em-adocao` → `ativo` → `expansao` → `fidelizado`

> Comercial volta a atuar aqui apenas em **expansões grandes** (não upsells operacionais — esses são CS). Pipelines one-off do tenant PD `pd-onboarding` e `pd-sucesso` detalham a operação de entrega.

---

## Métricas e definições críticas

- **MQL** = Reunião agendada com Closer (`reuniao-agendada-mql`).
- **SQL** = Reunião realizada (`reuniao-realizada-sql`).
- **Meta SDR (Mafê):** baseada em **SQL** (não MQL).
- **Funil alvo:** 200 leads novos/mês → 29 conversas → 14 quentes → 10 reuniões → ~3 fechamentos.

---

## Convenções de movimentação

1. **Sistema Comercial PD / cadências** move stages automaticamente baseado em sinais (resposta, evento, timing). Triggers de stage são **⏳ a construir (CAD-581)**.
2. **Movimentação manual** (operação atual): registrar motivo em **nota no contato** (`/api/app/contacts/[id]/notes`). Touchpoints via `/api/app/contacts/[id]/activities`.
3. **Toda mudança de stage** alimenta a `timeline_activities` do contato (feed cronológico — UI **⏳ a construir (CAD-576)**).
4. **StandBy ≠ Desqualificado.** StandBy retoma cadência após período. Desqualificado (`is_icp=false`) sai do funil.

---

## Acesso via API (Claude Code / automações)

**Backend:** Supabase Cadencia ref `elefbabxkaigusjiiflu` (produção = branch `master`).
**Tenant PD:** `6bb2c1ba-7fb3-416a-b523-7c9561ea8db3`.
**Auth interna (app):** JWT do usuário + `resolveTenant()`. **Auth externa (agente/automação):** HMAC-SHA256.

Operações comuns:
```
# Buscar contato (não duplica — bloqueia por email/telefone)
GET /api/app/contacts/search?q=<nome|email|telefone>

# Criar contato
POST /api/app/contacts   body: { first_name, last_name, email, phone, ... }

# Registrar touchpoint manual (call.made, email.sent, whatsapp.sent, ...)
POST /api/app/contacts/[id]/activities

# Mover oportunidade entre stages (automação externa / agente IA) — ⏳ a construir (CAD-582)
POST /api/v1/automations/move-card
headers: X-Tenant-Id, X-Timestamp, X-Idempotency-Key, X-Signature (HMAC-SHA256)
body: { contact_external_id, pipeline_slug, stage_slug, reason, metadata }
```

> Endpoints e contratos estão na documentação do CRM Cadencia.

---

## Refs

- `cadencia-10d.md` — fluxo da cadência 10D nos funis Demanda
- `playbook-objecoes.md` — quebra de objeções nos stages `em-conversa`, `call-realizada-qualificacao`, `negociacao-follow-up`
- `programa-indicacao.md` — leads de indicação entram em `geracao-demanda`/`novos-leads`
- `../context/stack-tecnico.md` — implementação técnica do Sistema Comercial PD
</content>
