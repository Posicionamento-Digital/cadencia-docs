---
date: 2026-05-25
tags: [ia, framework, pd, time, comercial]
moc: "[[MOC-IA-Tecnologia]]"
---

# PD Framework — Time Comercial

> Documentação humana do bootstrap. Fonte canônica: `pd-framework/times/comercial/`
> Linear: [PDL-262](https://linear.app/posicionamento-digital/issue/PDL-262) (bootstrap) · [PDL-263](https://linear.app/posicionamento-digital/issue/PDL-263) (Blueprint Sistema Comercial PD) · [PDL-264](https://linear.app/posicionamento-digital/issue/PDL-264) (Implementação Fase 1)
> Commits: `a5f7eed` (bootstrap) · `6eace35` (comercial-debate + PERSONAS + Linear issues) · `bc17810` (confirmação inspirações)

## Função do Time

Prospectar, qualificar, fechar e gerar indicações para PD Consultorias (ticket a partir de R$40k) e PD Gestores IA Franquia (R$15k em 3 meses). **Cadência SaaS NÃO entra aqui** (tem motor próprio self-serve R$119-499/mês via lançamentos/NoCode Startup/parcerias). Operação solo (Felipe Closer único) com plano de automação pesada via **Sistema Comercial PD** a construir (Docker container na VPS Master, stack nova, sem reaproveitar framework de terceiros). Espelha 100% os 3 pipelines reais do GHL (Enriquecimento + Geração de Demanda + Geração de Negócios). Nutrição fica em `times/marketing/nutricao/` — Comercial recebe leads quando viram **Hot** via handoff explícito.

## Estrutura

```
times/comercial/
├── CLAUDE.md (líder: Eduardo — inspiração Cauduro/SLG)
├── foundation/ (10 docs constitutivos)
│   ├── README.md
│   ├── icp-comercial.md           (3 trilhas Marketing + BANT por trilha)
│   ├── anti-icp-comercial.md      (sinais desqualificação + protocolo no-show D+0 a D+7)
│   ├── rep-g.md                   (framework PD próprio v2 — G1-G5)
│   ├── pipeline-structure.md      (3 pipelines GHL + critérios entre stages + handoff)
│   ├── playbook-objecoes.md       (top objeções por trilha + quebras)
│   ├── cadencia-10d.md            (3 fases × 3 trilhas × 7 touchpoints)
│   ├── programa-indicacao.md      (Lead ID + 90d + comissão escalonada)
│   ├── principios-cauduro.md      (criança 8 anos / 20×5 / alavancagem)
│   ├── rituais-solo.md            (Daily Stamper + Weekly + Forecast mensal)
│   └── decisions.md
├── context/
│   └── stack-tecnico.md           (blueprint Sistema Comercial PD a construir)
├── skills/
│   ├── consultar-rep-g.md         (consulta G1-G5)
│   ├── consultar-objecao.md       (busca objeção + script de quebra)
│   └── comercial-debate.md        (party mode Eduardo + Mafê + Roberto)
├── memory/
│   ├── STATE.md                   (L1 status / L2 progresso + agregado sub-squads / L3 Onboarding)
│   └── decisions.md               (D01-D07 append-only)
├── geracao-de-demanda/            (persona Mafê — LDR+SDR+BDR consolidado)
│   ├── CLAUDE.md
│   ├── memory/STATE.md + decisions.md
│   ├── skills/abordagem-rep-g.md + README.md
│   ├── workers/README.md          (roadmap workers — Sistema Comercial PD)
│   └── context/pipelines-demanda.md
└── geracao-de-negocios/           (persona Roberto — Closer)
    ├── CLAUDE.md
    ├── memory/STATE.md + decisions.md
    ├── skills/
    │   ├── framework-call-vendas.md  (7 partes Challenger)
    │   ├── fup-pos-reuniao.md        (D+1 a D+10 pós-proposta)
    │   ├── diagnostico-objecoes.md   (objeção real vs superficial)
    │   └── README.md
    └── context/pipelines-negocios.md
```

**2 sub-squads**, espelhando exatamente os pipelines reais do GHL (Geração de Demanda + Geração de Negócios). Pipeline Enriquecimento entra como pré-cadência dentro de `geracao-de-demanda/`.

## Personas

| Persona | Squad | Inspiração | Voz |
|---|---|---|---|
| **Eduardo** | Time Comercial (líder + facilitador) | Eduardo B. Cauduro (SLG, "Como Montar um Time de Vendas que Fatura Milhões" — Excepcionais Podcast 25/05) | Pragmática, alavancagem do gestor (Andrew Grove), "se falou e não escreveu, não falou", processo como instrução pra criança de 8 anos. Arbitra com lente de pipeline integral |
| **Mafê** (Maria Fernanda) | Geração de Demanda | **Aaron Ross** (Predictable Revenue — split SDR/LDR como sistema, cold calling 2.0) + **Jeb Blount** (Fanatical Prospecting — regra dos 30 dias, multicanalidade, playbook tático) | "Pipeline frio hoje = receita zero amanhã. 200 leads/mês alvo. Triangula canais sem virar spam. REP-G sem pular etapas." Quer **volume** entrando no funil |
| **Roberto** | Geração de Negócios (Closer) | **Chris Voss** (Never Split the Difference — *tactical empathy*, *mirroring*, *labeling*, *calibrated questions*; "no" como porta aberta) | "Não desperdiça reunião. Se lead não cabe, devolvo o tempo dele. Valor antes de preço. Framework Call 7 partes sem pular." Quer **leads aprofundados em qualificação** (BANT validado) |

**Tensão produtiva central** (registrada em `/comercial-debate`): Mafê quer volume × Roberto quer qualificação. Eduardo arbitra com lente de pipeline saudável (nem só topo, nem só fundo).

## Foundation docs (com status)

| Doc | Status | Conteúdo principal |
|---|---|---|
| `icp-comercial.md` | ✅ populado | 3 trilhas (PD Consultorias / Cadência SaaS / PD Gestores IA) herdadas do Marketing + BANT por trilha + 5 perguntas-chave de pré-call SDR + critérios CRM |
| `anti-icp-comercial.md` | ✅ populado | Sinais de desqualificação por trilha + protocolo no-show 7 dias (D+0 WhatsApp → D+1 ligação → D+2 WA → D+3 email → D+5 WA → D+7 encerramento) + reinício após 7d silêncio |
| `rep-g.md` | ✅ populado | Framework PD próprio v2 — 5 graus de confiança (G1 Conexão → G2 Curiosidade → G3 Relevância → G4 Valor → G5 Conversa). Mapa REP (Recognize/Elevate/Propose) distribuído nos graus. Personalização por nicho (clínicas/estética/ortopedia/hospital/gastro/consultores/e-commerce/SaaS/B2B) |
| `pipeline-structure.md` | ✅ populado | 3 pipelines GHL ativos (Enriquecimento + Geração de Demanda 11 stages + Geração de Negócios 5 stages) com critérios entrada/saída + handoff Demanda→Negócios via SQL + handoff Marketing→Comercial via Hot |
| `playbook-objecoes.md` | ✅ populado | Objeções universais (preço/timing/autoridade/concorrência/conhecimento) + específicas por trilha (PD Consultorias: "não tenho tempo"; PD Gestores IA: "será que funciona pra mim?") + princípios de quebra (empatia + reframe + custo da inação) |
| `cadencia-10d.md` | ✅ populado | Cadência intensiva 10 dias × 7 touchpoints × 3 trilhas. 3 fases (Intensiva D1-3 / Valor+Provocação D4-7 / Encerramento D8-10). Substituiu cadência 30D em 10/04/2026. Capacidade alvo: ~200 leads/mês → ~10 reuniões/mês |
| `programa-indicacao.md` | ✅ populado | Lead ID formato `LEAD-AAAAMMDD-XXXX` + janela 90 dias + comissão escalonada (10% <R$10k / 5% R$10-30k / 7% R$30-50k / 5% R$50-70k / 3% R$70-100k / fee custom acima) + comprovação obrigatória contrato+NF |
| `principios-cauduro.md` | ✅ populado | 10 princípios adaptados solo+automação (atuação alavancada / "se falou não escreveu não falou" / criança 8 anos / 20×5 bate 100×1 / especialização gera escala / comissionamento como comunicação / documentar antes de contratar / ciclo trimestral / alta performance angular / IA em vendas 2 usos maduros) |
| `rituais-solo.md` | ✅ populado | Daily Stamper (existe) + Weekly Comercial (sexta 17h — implementar) + Forecast mensal (última 6ª — implementar) + Pipeline Review (quarta 10h — implementar) + Call Review IA (gap roadmap) + Chat Review automático (gap roadmap) |
| `README.md` | ✅ populado | Índice + tabela "asset → leia primeiro" + frameworks de base (REP-G, Cauduro/SLG, Jeb Blount, Challenger Sale, Osterwalder VPC) |

**Nenhum doc EM REVISÃO ou ADIADO** — todos populados com dados reais (sem placeholders).

## Decisões chave (top 7 do decisions.md)

- **2026-05-25 — D07 Sistema Comercial PD construído do zero, Docker VPS Master** — sem reaproveitar framework de terceiros. Deploy: `master@72.60.4.71` user master/felipe. Stack a definir no blueprint (PDL-263). Squad nasce em modo "operação manual + plano de automação". Skills locais GHL (`ClaudeCode/Comercial/.claude/skills/`) continuam ativas como ferramentas auxiliares.
- **2026-05-25 — D06 Nutrição é Marketing** — pipeline GHL Nutrição (Hot/Quente/Aquecendo + scoring) e cadência 60d pós-tentativa vivem em `times/marketing/nutricao/`. Comercial recebe leads quando viram Hot via handoff explícito.
- **2026-05-25 — D05 Cadência SaaS tem motor próprio, fora do Time Comercial** — Comercial vende PD Consultorias (R$40k+) e PD Gestores IA (R$15k). Futuramente Cadência absorverá feature LDR/enriquecimento via roadmap do produto Cadência.
- **2026-05-25 — D04 Cadência ativa 10D (substituiu 30D em 10/04)** — capacidade aumentou de ~55 leads/mês para ~200 leads/mês com 50 ações/dia.
- **2026-05-25 — D03 Trilhas adotadas herdam Marketing** — PD Consultorias / Cadência SaaS / PD Gestores IA Franquia (em `times/marketing/foundation/icp.md`). Trilhas antigas do wiki Notion (Consultoria/Ferramentas IA/Franquia genéricas) viram histórico.
- **2026-05-25 — D02 Estrutura espelha pipelines GHL** — 2 sub-squads: `geracao-de-demanda/` (cobre Enriquecimento + Geração de Demanda + handoff de Hot) e `geracao-de-negocios/` (cobre Geração de Negócios + Programa Indicação).
- **2026-05-25 — D01 Eduardo como persona líder do Time** — homenagem a Eduardo B. Cauduro. Sub-squads: Mafê (Geração de Demanda) e Roberto (Geração de Negócios). Inspirações Mafê (Ross + Blount) e Roberto (Voss) confirmadas após bootstrap.

## Pessoas-chave

- **Felipe** — Closer único + operador solo + arquiteto/dev futuro do Sistema Comercial PD
- **Mateus** — referência histórica de BDR (humano que executou cold outbound REP-G no passado, validou padrão "Indicação + Ferramenta Específica" registrado em `rep-g.md`). Não está mais no time.
- **Sandro/Vanessa** — parceiros CRM-PD (programa indicação ativo)
- **Romulo Navajas** (Azoto Anestesia) — indicação validada (caso Sabrina/One Medical Group em `rep-g.md`)
- **Nathalia** — consultora indicada
- **Marina** — lead/parceira ativa
- **Time GO (GCI)** — referência indireta (Lara opera GHL de outro produto)

## Projetos Linear vinculados

- **PDL-262** — [Times] Bootstrap Time Comercial — sessão criação com Felipe — ✅ **Done** (esta sessão)
- **PDL-263** — [Comercial] Blueprint Sistema Comercial PD — Docker VPS Master — 🔵 Backlog (filha de PDL-262)
- **PDL-264** — [Comercial] Implementação Fase 1 — Sistema Comercial PD — 🔵 Backlog (filha de PDL-263, bloqueada por PDL-263)
- **Comercial — Felipe** (`349375b6`) — projeto guarda-chuva do Time (issues específicas usam label `squad:times/comercial/geracao-de-demanda` ou `squad:times/comercial/geracao-de-negocios`)
- **Proposta Grupo WGL — Energia B2B** (`8bddc558`) — deal aberto R$68k+ → `times/comercial/geracao-de-negocios`

Mapeamento cascata: `_core/linear-squad-map.json`. Label workspace: `squad:times/comercial`.

## Deals abertos atuais

- **Mlau Fernandes** (vereadora Mogi) — R$ 68.6k — campanha eleitoral 2026 — em `geracao-de-negocios` (memory `project_mlau_fernandes_lead_70k`)
- **Grupo WGL Enterprise** — R$ 68k+ — energia B2B — em `geracao-de-negocios` (memory `session_meeting_transcriber_wgl_2026_05_19`)

## Bloqueios externos

- **Sistema Comercial PD não existe ainda** — operação manual no GHL até PDL-264 entregar. Capacidade limitada a ~50-80 leads/mês até automação rodar.
- **Reconstrução GHL pós-takeover Michael (07/05)** em andamento em `ClaudeCode/Comercial/`. Migração final das 7 subcontas pra nova agência `rIrmvD1WcDqVNAyDRnf8` (plano SaaS Pro) ainda pendente. Não bloqueia Squad, mas é dependência adjacente.
- **2 PITs órfãos GHL** retornam 401 — revogar quando recuperar agency-owner antigo.
- **Workflows GHL** (84 total entre subcontas) precisam ser recriados manualmente na nova agência (snapshot path morto pós-takeover).

## Como usar

- **Abrir:** `/abrir-squad times/comercial`
- **Debate:** `/comercial-debate` (Eduardo facilita + Mafê voz demanda + Roberto voz negócios — tensão volume × qualificação explicitada)
- **Personas invocáveis:** `/eduardo` (decisão cross-funil), `/mafe` (prospecção, cadência 10D, abordagem REP-G G1-G2), `/roberto` (call de vendas, proposta, FUP, fechamento)
- **Skills Time-level:**
  - `/consultar-rep-g` — pergunta sobre G1-G5, lê foundation/rep-g.md
  - `/consultar-objecao` — busca objeção + script de quebra, lê foundation/playbook-objecoes.md
- **Skills Geração de Demanda:**
  - `/abordagem-rep-g` — gera mensagem G1 personalizada cold outbound (input: nome+empresa+canal+trilha+contexto pesquisado)
- **Skills Geração de Negócios:**
  - `/framework-call-vendas` — guia 7 partes (consultar antes/durante call)
  - `/fup-pos-reuniao` — cadência D+1, D+3, D+5, D+7, D+10 pós-proposta
  - `/diagnostico-objecoes` — identifica objeção real vs superficial
- **Skills auxiliares** (vivem em `ClaudeCode/Comercial/.claude/skills/`): `proposta-comercial-pd`, `agendar-call`, `analise-funil-ecuro`, `criar-user-ghl`

## Pendências pra sessões futuras

- **PDL-263 (Blueprint Sistema Comercial PD)** — definir stack (linguagem, backend, queue, banco), arquitetura de pastas, schema do banco, paths na VPS Master, integrações externas (GHL, DataStone B2C+B2B, Perplexity Sonar, CNPJ.ws, Stevo)
- **PDL-264 (Implementação Fase 1)** — workers + cadência 10D + container Docker + cron diário 8h BRT + scoring webhook
- **Sessões dedicadas pra popular profundamente** personas Mafê e Roberto (hoje têm CLAUDE.md de bootstrap, falta voz própria detalhada e scripts característicos)
- **Gaps Cauduro como roadmap futuro (issues Linear)**:
  - Resposta inbound instantânea com IA (Layla-style) — atende lead form/Instagram/WhatsApp em <1min
  - Análise automática de gravações de call com IA — cruza com REP-G + Challenger, gera feedback
- **Migração GHL pós-takeover finalizar** — workflows recriados, PITs órfãos revogados (dependência `ClaudeCode/Comercial/`)
- **Decisão sobre centralizar skills GHL** (`ClaudeCode/Comercial/.claude/skills/` → `times/comercial/geracao-de-negocios/skills/`)

## Notas relacionadas

- [[IA-Tecnologia/2026-05-25 PD Framework — Hierarquia Time-Squad e memory híbrida]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Constituição dos Times]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Arquitetura DEFINITIVA consolidada]]
- [[IA-Tecnologia/2026-05-25 PD Framework — Time infra]] — Time-modelo (referência paralela)
- [[IA-Tecnologia/2026-05-25 PD Framework — Time Dev]] — Time-modelo (referência paralela)
- [[IA-Tecnologia/2026-05-24 PD Framework — Mapa final e decisões consolidadas]]
- [[Estudo/Vendas/2026-05-25_como-montar-time-vendas-fatura-milhoes]] — base do framework Cauduro absorvido na sessão
