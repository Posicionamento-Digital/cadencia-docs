---
date: 2026-06-27
tags: [doc, componente, cadencia-growth]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
---
# cadencia-growth → scoring/

2 daemons HTTP recebendo webhooks externos.

## Identidade
- **Tipo:** daemons HTTP
- **Stack:** Python 3.12 · http.server stdlib · svix
- **Path:** `scoring/`
- **Portas:** `:8766` (GHL) + `:8767` (Resend)
- **Status:** ativo

## Arquivos
- `webhook_handler.py` :8766 — GHL agency webhook (EmailOpen/Click → score_ia/temperature/tags em Supabase)
- `resend_webhook.py` :8767 — Resend Svix-signed webhook (mesmo scoring)

## Auth
- GHL: header signature validation
- Resend: HMAC Svix com `RESEND_WEBHOOK_SECRET`

## Don'ts
- Não confiar payload sem validar signature
- Não escrever direto na `contacts` fora do scoring

## Notas Relacionadas
[[Projetos/Cadencia-Growth/Docs/README]] · [[Projetos/Cadencia-Growth/Docs/pipeline]]