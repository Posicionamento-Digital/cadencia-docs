---
date: 2026-07-04
tags: [doc, documentacao, projeto, observabilidade]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[Central de Observabilidade]]"]
---
# Botão de ajuda → Central de Observabilidade (DEV-1085)

## TL;DR
Ticket criado pelo FeedbackButton (`POST /api/app/tickets`) com type `bug` ("Algo não funcionou") ou `broken_feature` ("Função com problema") é encaminhado assinado pra bridge da Central, que cria issue `tipo:suporte` + `own:felipe` no Linear (projeto *maint: Cadência*) com dedup e WhatsApp.

## Fluxo
1. Usuário envia o report → insert em `support_tickets` (comportamento original intacto).
2. A rota POSTa pro `https://sentry-bridge.cadencia.app.br/support-webhook` com HMAC sha256 do body no header `x-support-signature` (env `SUPPORT_WEBHOOK_SECRET` — 1P `Cadencia Bridge - SUPPORT_WEBHOOK_SECRET [ClaudeCode]`, mesma env no Coolify da bridge e no Vercel).
3. Bridge (repo `Posicionamento-Digital/health-check`, `bridge/app/main.py`): dedup `[support:<sha1(tenant|option|message)[:10]>]` → issue no Linear → WhatsApp best-effort.
4. **Fail-open**: bridge fora do ar NUNCA quebra a criação do ticket (try/catch + timeout 5s + `console.error` com prefixo `[DEV-1085]`).

## Escopo
- `missing_feature` ("Falta uma função") fica **só** na tabela — decisão de escopo da issue.
- Report de usuário NUNCA vai direto pra `own:agente` — triagem humana decide se é bug.

## Payload (contrato com a bridge)
```json
{"tenant_id","user_email","option":"bug|broken_feature","message","page","meta":{"ticket_id","component_path"}}
```

## Troubleshooting
- **Issue não criada mas ticket sim** → ver logs da função (`[DEV-1085] support forward fail-open`) e `/health` da bridge; conferir env `SUPPORT_WEBHOOK_SECRET` nos dois lados (401 = assinatura).
- **Issue duplicada não aparece** → é o dedup por conteúdo (mesmo tenant+option+message) — comportamento desenhado.

## Histórico
- 2026-07-04 — criado (PRs #110/#111 + bridge PRs #4/#5). E2E produção: DEV-1180 criada automaticamente a partir de ticket real.


## Notas Relacionadas
[[audit-cross-tenant]]
