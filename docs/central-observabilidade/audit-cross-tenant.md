---
date: 2026-07-04
tags: [doc, documentacao, projeto, observabilidade]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Central de Observabilidade]]"]
---
# Audit de mutações multi-tenant (DEV-934)

## TL;DR
Toda mutação via admin client (service_role, que bypassa RLS) pode ser auditada trocando `createAdminClient()` por `createAuditedAdmin(ctx)` — grava em `audit_log_tenant_writes` e, se o tenant gravado divergir do tenant ativo da sessão, dispara `Sentry.captureMessage` → Central de Observabilidade (issue Linear + WhatsApp).

## Por que existe
A investigação DEV-933 provou que o stack (Sentry/PostHog/Mixpanel) **não detecta** vazamento de contexto multi-tenant: super_admin/impersonate gravando no tenant errado não gera exception nem evento. Este audit é a rede de detecção; a RLS de WRITE (bloqueio na origem) é etapa 2, calibrada com os dados daqui.

## Como funciona
- `src/lib/supabase/audit.ts` — `createAuditedAdmin(ctx)` devolve um Proxy do admin client:
  - intercepta `insert/update/upsert/delete`; `select` passa direto, sem custo;
  - tenant do payload (insert/upsert) OU do filtro (`.eq/.match/.in/.filter` em `tenant_id`);
  - lote com tenants mistos (ou row sem tenant) vira `MULTIPLE` — nunca mascara;
  - **fail-open absoluto**: erro do audit loga `[DEV-934]` e nunca bloqueia a mutação;
  - gravação fire-and-forget (client singleton dedicado, sem await no hot path).
- `ctx` é mutável de propósito: crie antes do `resolveTenant`, preencha `ctx.activeTenant` depois do guard.
- Migration `20260704210000` — tabela com RLS service-only + view `cross_tenant_writes_24h` (**meta = 0**) com `security_invoker = true` + revoke `anon`/`authenticated` (sem isso o PostgREST exporia o audit — P1 pego no claude-review de 04/07).

## Adoção (incremental, 1 linha por rota)
```ts
const auditCtx: AuditCtx = { route: "/api/app/x", userId: user.id, activeTenant: null,
  requestId: request.headers.get("x-request-id") ?? randomUUID() };
const admin = createAuditedAdmin(auditCtx);
const role = await resolveTenant(admin, user.id);
// ...guard...
auditCtx.activeTenant = role.tenant_id;
```
Adotadas (04/07): `/api/app/trigger-generation` (cobre até as mutações internas do `debitCredits`) e `/api/app/tickets`. **Pendente:** demais rotas de mutação das tabelas críticas + adotar o `tenant-guard.ts` (CAD-599 — existe e está órfão, zero imports) nos jobs service_role.

## Don'ts
- NUNCA `await` no insert de audit dentro do hot path.
- NUNCA expor a tabela/view pra `anon`/`authenticated` (revoke é parte da migration).
- Rota nova de mutação SEM o wrapper nasce sem audit — cobrar na adoção.

## Consultas úteis
```sql
select * from cross_tenant_writes_24h;                         -- meta = 0
select route, count(*) from audit_log_tenant_writes group by 1; -- cobertura por rota
```

## Testes
`src/lib/supabase/audit.test.ts` — 13 casos (mismatch por payload e por filtro, MULTIPLE, select transparente, retorno preservado). `npx vitest run src/lib/supabase/audit.test.ts`.

## Histórico
- 2026-07-04 — criado (PR #112, cascata crítica: openrouter + claude-review + runtime-fix-review). E2E produção: linha real com `request_id` propagado, view = 0.


## Notas Relacionadas
[[suporte-botao-ajuda]]
