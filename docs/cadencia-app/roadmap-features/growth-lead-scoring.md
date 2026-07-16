---
date: 2026-05-19
tags: [documentacao, cadencia, growth, lead, scoring, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]", "[[marketing]]"]
---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

## Identidade
- **Tipo:** feature Growth — scoring de leads
- **Stack:** Python 3.12, HTTPServer, GHL API
- **Path no repo:** `cadencia-growth/scoring/webhook_handler.py`
- **Status:** Produção — webhook rodando, scoring básico ativo

## O que é
Servidor HTTP na porta 8766 que recebe eventos de comportamento de leads e atualiza o campo `score_ia` no contato GHL. Multi-tenant via `location_id` no `tenant_config`.

## Tabela de pontos atual
- email_opened / email_open → +2
- link_clicked / email_clicked / link_click → +5

## Como funciona
Payload com locationId + contactId + type → busca tenant pelo location_id → GET score atual → PUT score + delta.

## O que ainda não está portado do PD Marketing
- Pipeline movement (mover contato entre stages por threshold)
- Mais eventos (newsletter, WhatsApp, SOAP)
- Tabela scoring_events para auditoria
- Inatividade job (decay de -10 após 30 dias)

## Notas Relacionadas
[[growth-email-dispatch]] · [[growth-newsletter]]
