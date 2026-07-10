> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/adr/0006-multi-tenant-rls-supabase.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0006-multi-tenant-rls-supabase.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# ADR-0006 — Multi-tenant via RLS Supabase (não DBs separados)

**Status:** aceito · **Data:** 2026-05-27

## Contexto

Cadência é SaaS multi-tenant — múltiplos clientes, dados completamente isolados, mas operados pela mesma stack. Opções de isolamento:

1. **DB por tenant** — máxima isolação, complexidade operacional explosiva.
2. **Schema por tenant** — meio termo, mas migrações N vezes mais lentas.
3. **Tabela única + RLS (Row Level Security)** — simples, escala bem, depende de policies corretas.

## Decisão

Tabela única + RLS Supabase. Todas as tabelas com dados de tenant têm `tenant_id` UUID e policies RLS que filtram por `auth.uid()` → `user_tenant_roles.tenant_id`.

Policies otimizadas em PDL-159 a PDL-166 (2026-05-19) — substituíram `auth.uid()` por `(SELECT auth.uid())` para evitar reavaliação por linha.

`service_role` bypassa RLS — usado pelos workers/VPS scripts para operações cross-tenant (cron diário).

## Consequências

- ✅ Migration única afeta todos os tenants.
- ✅ Custo Supabase linear com volume, não com número de tenants.
- ✅ Backup/restore único.
- ❌ Erro em policy RLS = vazamento entre tenants. Auditoria contínua obrigatória.
- ❌ Performance sensível à qualidade da policy — `auth.uid()` direto na policy degrada queries em escala (resolvido PDL-159+).
- ⚠️ Workers e VPS scripts usam `service_role` — qualquer SQL injection ali vaza dados entre tenants.

## Não considerado

- DB por tenant — custo Supabase × N + complexidade migrações.
- Schema por tenant — Supabase suporta mal, e migrations escalam mal.

## Referências

- `supabase/migrations/20260519170000_optimize_rls_policies.sql` (otimização)
- `times/produto/cadencia/foundation/multi-tenant-strategy.md`
