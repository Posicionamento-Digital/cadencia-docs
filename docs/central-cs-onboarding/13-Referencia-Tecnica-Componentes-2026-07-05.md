---
date: 2026-07-05
tags: [documentacao, projeto, cs, arquitetura]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central CS Onboarding]]", "[[comercial]]"]
---
# Central de CS — Referência Técnica por Componente (05/07/2026)

> Gerado por `/documentar` sobre o knowledge-graph atualizado (camada "Central de CS", 44 nós, commit 5cfed981). A doc técnica completa vive **no repo** (`times/cs/docs/`) — esta nota é o índice navegável + visão de arquitetura. Não duplica o conteúdo dos componentes.

## O que é a Central de CS

Subsistema que automatiza o ciclo do cliente do fechamento comercial ao acompanhamento. Código quase todo em `_shared/` (helpers determinísticos); `times/cs/` guarda manuais e workers. Padrão: **gatilho → orquestrador determinístico → efeito idempotente → alerta ao Felipe**.

## Jornada de um cliente (end-to-end)

1. **Fechamento** → contrato emitido (frontmatter: parcelas, créditos, asaas_customer_id, t0)
2. **Assinatura** → `contrato_autentique_sync` promove status consultando Autentique ao vivo
3. **Consolidação Fase 1** → `consolidador_onboarding`: Asaas (reconcile tolerante) + CRM + tenant + Manual
4. **T-0** = 1ª parcela paga → libera implantação + alimenta ciclo de recarga
5. **Briefing/Kickoff** → transcrição local (WhisperX) → inbox VPS Dev
6. **Cadeia pós-briefing** → extração LLM → grupo WhatsApp → Manual da Marca → entrega dual-canal (após revisão do Felipe)
7. **Acompanhamento** → workers cron: cobrança, aprovação tácita, confirmação de agenda, aquecimento, **recarga de créditos (produção real)**

## Os 7 componentes (doc completa no repo)

| # | Componente | Doc no repo |
|---|---|---|
| 1 | Onboarding & Consolidação | `times/cs/docs/01-onboarding-consolidacao.md` |
| 2 | Contratos (parse + Autentique + fases) | `times/cs/docs/02-contratos.md` |
| 3 | Billing (Asaas, reconcile tolerante) | `times/cs/docs/03-billing-asaas.md` |
| 4 | Cadeia pós-briefing (o coração) | `times/cs/docs/04-cadeia-pos-briefing.md` |
| 5 | Stakeholders & Matriz (PJ + PF) | `times/cs/docs/05-stakeholders-matriz.md` |
| 6 | Comunicação & Auto-log | `times/cs/docs/06-comunicacao-clients.md` |
| 7 | Workers (cron) | `times/cs/docs/07-workers.md` |
| — | Arquitetura (C4 mermaid) | `times/cs/docs/architecture.md` |
| — | Linguagem ubíqua | `times/cs/docs/CONTEXT.md` |

## Decisões arquiteturais-chave

- **Determinístico no meio, LLM nas pontas** — orquestração é script puro (VPS Master); extração e Manual da Marca são LLM (VPS Dev). SECURITY §1.
- **Idempotência universal** — marker na timeline CRM, hash de arquivo, dedup Asaas.
- **Reconcile tolerante** (CSE-92) — parcela reemitida não duplica cobrança; billing nunca duplica.
- **Auto-log no client, não nas skills** (CSE-100) — nada que sai pro cliente escapa da timeline.
- **Grupo automático + Manual da Marca** na cadeia pós-briefing (CSE-99/101).

## Explorar interativo

`/understand-dashboard` → camada "Central de CS (Automação de Onboarding)" + tour de 12 passos que percorre a cadeia pós-briefing.

## Notas Relacionadas
[[Projetos/Central CS Onboarding/Docs/00-Visao-Geral]] · [[Projetos/Central CS Onboarding/Docs/12-Hardening-Billing-Observabilidade-2026-07-04]] · [[Projetos/Central CS Onboarding/Docs/04-Consolidador]]
