---
type: source
source_kind: decisao
date: 
entities: ["[[Cadencia]]", "[[produto]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Decisões — produto-consultorias-iasmim-lopes-memory

# Decisions — Iasmim Lopes

## 2026-07-06 — Piloto com escrita real na conta de um terceiro (Ageu) via preview descartável

**Contexto:** a Manuela concedeu acesso de parceiro à conta de anúncios do cliente-corretor **Ageu Ribeiro** (não da própria Brokers). Pra a cliente testar de verdade, era preciso sair do modo fixtures — o que liga escrita real (pausar/escalar/segmentação/criar campanha) numa conta com campanhas ativas gastando dinheiro real de um terceiro.
**Decisão:** Felipe autorizou **liberar apply/escrita real** (não read-only) desde já. `TRAFEGO_DEMO_FIXTURES=0`, conta do Ageu plugada no preview `feature/dev-1070` (branch descartável, não mergeada). Toda ação tem modal de confirmação; nada executa sozinho. Manual de uso publicado no Quartz destacando que as ações valem de verdade na conta do Ageu.
**Alternativas consideradas:** travar em só-leitura primeiro (descartado por Felipe — quer o teste completo); esperar a arquitetura de produto Composio (descartado — piloto informa o que reabrir dos epics cancelados).
**Impacto:** piloto de 1 semana (até 13/07) com feedback via Tally (CSE-104); risco operacional de a cliente alterar campanha ativa de terceiro sem querer (mitigado por modal + aviso no manual); monitor E2E do acesso Meta proposto (DEV-1211, ainda não construído); contrato segue sem assinatura.
**Quem decidiu:** Felipe.

## 2026-07-03 — Acesso preview entregue antes da assinatura do contrato

**Contexto:** demo apresentada 03/07 17h; Felipe quis dar acesso hands-on à cliente na sequência. Contrato ainda sem assinatura (Iasmin pediu ajuste) — a regra padrão (contrato antes de provisionar, furo Juliana 29/06) foi levantada como gate.
**Decisão:** Felipe autorizou explicitamente entregar o acesso preview mesmo sem assinatura ("sim, depois vamos fazer a assinatura"). Tenant próprio (20 créditos, login único da Iasmin), modo fixtures (sem dados/escrita reais), conta Meta real só após acesso de parceiro concedido pela Manuela.
**Alternativas consideradas:** segurar até assinar (descartado — momentum pós-demo vale mais; exposição limitada por fixtures); conectar a conta Meta dela já (descartado — depende de ação dela no BM; caminho documentado em manual público).
**Impacto:** gate multi-tenant no código da demo (`gate.ts`, lista em `TRAFEGO_DEMO_TENANT_ID`); tenant demo vivo no Cadencia; pendência ativa de assinatura continua rastreada.
**Quem decidiu:** Felipe.
