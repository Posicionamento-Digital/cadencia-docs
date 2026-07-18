# api-auth-provisioning — auth e provisionamento de tenant

## TL;DR

`POST /api/auth/provision-tenant` cria o tenant do usuário autenticado e inicia
o provisionamento do CRM Cadencia, da carteira de créditos e dos recursos de
onboarding.

## Identidade

- **Tipo:** Next.js API Route
- **Path:** `src/app/api/auth/provision-tenant/route.ts`
- **Deps:** Supabase Auth + service role

## Fluxo

1. valida a sessão e o usuário;
2. cria ou recupera `tenants` e `users` de forma idempotente;
3. garante `user_tenant_roles` com papel owner;
4. cria `tenant_onboarding`;
5. cria a carteira inicial de créditos;
6. semeia pipelines, stages, tags e campos do CRM próprio;
7. dispara o provisionamento assíncrono de domínio Resend/DNS e artefatos.

## Don'ts

- Não criar um segundo tenant para o mesmo `auth_user_id`.
- Não expor `service_role` ao cliente.
- Não considerar o fire-and-forget como concluído sem observabilidade e retry.
- Não reduzir créditos existentes em retries.

## Validação

Validar signup novo, repetição idempotente, isolamento tenant, 20 créditos
iniciais e continuidade quando um provisionamento assíncrono falha.

## Referências

- [api-routes](../CLAUDE.md)
- [email-domain-provisioning](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/email-domain-provisioning.md)
