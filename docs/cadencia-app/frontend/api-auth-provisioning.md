> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/app/api/auth/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/app/api/auth/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# api-auth-provisioning — auth e provisionamento de tenant

## TL;DR

2 rotas críticas: `provision-tenant` (cria tenant no signup) e OAuth callback do GHL.

## Identidade

- **Tipo:** Next.js API Routes
- **Paths:**
  - `src/app/api/auth/provision-tenant/route.ts`
  - `src/app/api/growth/oauth/callback/route.ts`
- **Status:** ativo
- **Deps:** Supabase (service_role), Workers Coolify VPS Master (GHL signup)

## provision-tenant (POST /api/auth/provision-tenant)

Chamado no signup. Cria em sequência:
1. `tenants` (slug gerado do nome)
2. `users` (tabela pública, FK para auth.users)
3. `user_tenant_roles` (role: owner)
4. `tenant_onboarding` (phase: 1)
5. `tenant_plans` (trial, 3 créditos)
6. Fire-and-forget: `POST /api/v1/ghl/signup` nos workers → contato GHL na location central

## OAuth callback (GET /api/growth/oauth/callback)

- Troca `code` por tokens via `exchangeCodeForTokens(code, "Company")`
- Salva em `ghl_agency_oauth` via `saveAgencyOAuthTokens(companyId, tokens)`
- Necessário fazer 1x para desbloquear PDL-25

URL para completar OAuth (fazer 1x):
```
https://marketplace.gohighlevel.com/oauth/chooselocation?client_id=69f238fc0a7e8f7efa495682-mokblahu&redirect_uri=https://cadencia.app.br/api/growth/oauth/callback&scope=...
```

## Don'ts

- `provision-tenant` é idempotente? Verificar antes de chamar novamente para mesmo usuário
- `ghl_agency_oauth`: só deve ter 1 registro (company-level). Não criar duplicatas.

---

## Quando usar

- Signup novo usuário/tenant → `provision-tenant` cria tenant + plano trial.
- OAuth GHL Marketplace callback → desbloqueia `ghl_agency_oauth` (resolve PDL-25).

## Quando NÃO usar

- ❌ Chamar `provision-tenant` para tenant existente — verificar idempotência primeiro.
- ❌ Recriar registro em `ghl_agency_oauth` — só deve ter 1 (company-level).
- ❌ Bypassar verificação de email — Supabase Auth padrão.

## Por que funciona assim

- Provision cria toda a cadeia (`tenants → users → roles → onboarding → plan`) em transação — falha parcial = tenant órfão.
- Fire-and-forget para workers (GHL signup) — não bloqueia signup do usuário.
- OAuth Marketplace 1x: ato administrativo, não recorrente.

## 🚫 Don'ts

- **Não** chamar `provision-tenant` 2x para mesmo `auth_user_id` — duplica tenant.
- **Não** criar `ghl_agency_oauth` duplicado.
- **Não** ignorar erro do workers signup — ainda que fire-and-forget, deve logar para audit.
- **Não** salvar tokens OAuth em texto claro fora do `ghl_agency_oauth` (DB).

## 🪦 Já tentamos

- **2026-05-27 — Auth recovery token expirado update-password**: ver incident.
- PDL-25 bloqueia provisioning automático por falta de OAuth Marketplace completado.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Tenant duplicado | `provision-tenant` chamado 2x | Idempotência via `auth_user_id` lookup primeiro |
| OAuth callback retorna 500 | Code expirado / state mismatch | Refazer fluxo completo Marketplace |
| `ghl_agency_oauth` vazio | OAuth nunca completado (PDL-25) | Completar via URL Marketplace |
| Workers signup falha silencioso | Sem retry | Logar resposta + manual retry |

## 📚 Referências cruzadas

- [provisioning-ghl](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/provisioning-ghl.md) — Usa `ghl_agency_oauth`
- [api-routes](../CLAUDE.md)
- PDL-25 (Linear) — bloqueio OAuth
