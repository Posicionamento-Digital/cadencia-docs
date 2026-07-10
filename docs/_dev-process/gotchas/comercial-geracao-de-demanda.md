---
type: source
source_kind: gotcha
date: 
entities: ["[[Cadencia]]", "[[comercial]]"]
tags: [gotcha, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# Gotchas — comercial-geracao-de-demanda

# Gotchas — times/comercial/geracao-de-demanda

> Armadilhas técnicas validadas (manual review).
> Source: entries promovidas de gotchas-pending.md (auto-detect).

## CRM Cadencia: `opportunities move` exige UUID e não cria timeline de stage

**Sintoma:** usar `cadencia-cli opportunities move <opp> --to-stage tentando-contato` falha ou não deixa rastro completo de timeline.

**Causa:** o comando `opportunities move` espera UUID do stage, não slug. Além disso, ele atualiza `opportunities.stage_id`, mas não cria automaticamente a linha de timeline de movimentação.

**Como fazer:** resolver o stage com `cadencia-cli pipeline-stages list --pipeline geracao-demanda`, mover com UUID e depois registrar `cadencia-cli contacts activity <contact_id> --type opportunity.stage_moved ...`.

**Impacto:** sem a activity manual, a oportunidade fica no stage certo, mas a linha do tempo do contato não mostra a movimentação de funil.

## 1Password rate limit em consulta CRM em lote

**Sintoma:** depois de muitos `cadencia-cli contacts get`/`opportunities get` em sequência, o CLI falha com `Too many requests. Your client has been rate-limited` ao resolver `supabase_pat`.

**Causa:** cada comando do CLI busca a credencial no 1Password; loops rápidos batem limite do `op`.

**Como fazer:** preferir consultas SQL agrupadas quando possível, reduzir loops de comandos unitários e aguardar a janela do 1Password liberar antes de continuar. Se a credencial estiver bloqueada, não enviar WhatsApp sem validar contato/oportunidade no CRM.

**Impacto:** a sessão de 2026-07-07 enviou 7 leads e bloqueou a busca dos 2 substitutos por rate limit. Retomar só depois de validar os novos leads.
