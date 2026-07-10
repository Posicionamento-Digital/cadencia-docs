> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `supabase/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/supabase/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# supabase-schema — banco de dados (55 tabelas PostgreSQL)

## TL;DR

PostgreSQL via Supabase Cloud. 55 tabelas com RLS. Project ref: `elefbabxkaigusjiiflu`. Schema completo em `pd-framework/times/produto/cadencia/context/supabase-schema.json`.

## Identidade

- **Tipo:** PostgreSQL + Row Level Security
- **Project ref:** `elefbabxkaigusjiiflu`
- **URL:** `https://elefbabxkaigusjiiflu.supabase.co`
- **Migrations:** `supabase/migrations/*.sql`
- **Status:** ativo

## Tabelas-chave

| Tabela | O que guarda |
|---|---|
| `tenants` | Tenant cadastrado (slug, nome, status) |
| `users` | Tabela pública de usuários (FK para `auth.users`) |
| `user_tenant_roles` | Roles por tenant (owner, admin, member) |
| `tenant_config` | JSON config por tenant (GHL tokens, visual, flags, SOUL) |
| `tenant_plans` | Planos e créditos por tenant (pode ter múltiplos ativos) |
| `tenant_onboarding` | Fase atual do onboarding |
| `tenant_dossier` | Dossier de marca gerado pelos workers |
| `tenant_profile` | Big5 + DPR signaling consolidado |
| `profile_responses` | Respostas brutas do perfilamento |
| `editorials` | 3 editoriais por tenant |
| `content_ideas` | Ideias de conteúdo com `editorial_id` FK |
| `generation_queue` | Fila de geração (created/processing/completed/failed) |
| `content_documents` | Documento de conteúdo gerado (slides, rendering status) |
| `published_posts` | Posts publicados com todos os canais (blog, seinfeld, linkedin, instagram, newsletter) |
| `tenant_themes` | Cache do theme engine por tenant |
| `style_configs` | Configurações visuais por Big5 + signaling |
| `scoring_events` | Log de eventos de scoring (fire-and-forget) |
| `ghl_agency_oauth` | Token OAuth da agência GHL (company-level) — 1 registro |
| `api_call_logs` | Log de chamadas LLM (custo tracking) |

## Acesso

```bash
# Management API (DDL + DML)
gh api "repos/felipeluissalgueiro/cadencia-app/..." # não usar pra SQL

# Via Management API direta:
curl -X POST "https://api.supabase.com/v1/projects/elefbabxkaigusjiiflu/database/query"   -H "Authorization: Bearer <PAT>" -H "User-Agent: Mozilla/5.0"   -d '{"query": "SELECT ..."}'
# PAT: 1Password → vault databases → "Supabase - ClaudeCode - CLI" → credencial
```

## Don'ts

- Service_role bypassa RLS — nunca usar em código client-side
- Após CREATE TABLE via Management API: `NOTIFY pgrst, 'reload schema'` (PostgREST cache)
- `generation_queue.channel` vs `channels`: schema inconsistente (PDL-171 — verificar antes de alterar)

---

## Quando usar

- Toda persistência de dados do produto. 55 tabelas, RLS habilitado.
- Migrations: `supabase/migrations/*.sql` — versionado em git.
- Management API para SQL ad-hoc + analytics: `https://api.supabase.com/v1/projects/elefbabxkaigusjiiflu/database/query`.

## Quando NÃO usar

- ❌ Storage de imagens grandes (>10MB) — usar Supabase Storage, não tabela.
- ❌ Service_role em código client — bypassa RLS, vaza dados entre tenants.
- ❌ Migrations rodando direto em produção sem revisão — staging primeiro.

## Por que funciona assim

- [ADR-0006](../docs/adr/0006-multi-tenant-rls-supabase.md) — Multi-tenant via RLS, não DBs separados.
- Policies otimizadas em PDL-159 a PDL-166 (2026-05-19) — `(SELECT auth.uid())` em vez de `auth.uid()` para evitar reavaliação por linha.
- Schema completo em `pd-framework/times/produto/cadencia/context/supabase-schema.json`.

## 🚫 Don'ts

- **Não** rodar migration de RLS sem testar com tenant específico (caso `tenant_users` inexistente — ver incident).
- **Não** usar `auth.uid()` direto na policy — usar `(SELECT auth.uid())` para performance.
- **Não** esquecer `NOTIFY pgrst, 'reload schema'` após CREATE TABLE via Management API.
- **Não** confundir `generation_queue.channel` (singular antigo) com `channels` (plural novo) — PDL-171.

## 🪦 Já tentamos

- **2026-05-19 — Migration RLS tenant_users inexistente**: migration referenciava tabela que não existia naquele ambiente. Ver `2026-05-19_migration-rls-tenant-users-inexistente.md`.
- PDL-159 a 166 — otimizar RLS policies, drop unused indexes, drop realtime publication. Resultado: queries pesadas 10x mais rápidas.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Query degradou após policy nova | `auth.uid()` direto reavalia por linha | Reescrever com `(SELECT auth.uid())` |
| PostgREST 404 após CREATE TABLE | Schema cache stale | `NOTIFY pgrst, 'reload schema'` |
| Migration falha em produção | Tabela ref não existe / dependência ausente | Reverter + testar staging |
| Cloudflare 1010 ao chamar Management API | UA default Python urllib | Setar `User-Agent: Mozilla/5.0` |
| Vazamento entre tenants | RLS policy mal escrita | Auditar todas policies com `service_role` em mente |

## 📚 Referências cruzadas

- [supabase/migrations/](migrations/) — Migrations versionadas
- ADR: [0006 RLS multi-tenant](../docs/adr/0006-multi-tenant-rls-supabase.md)
- `pd-framework/times/produto/cadencia/context/supabase-schema.json` — Schema completo
- [CONTEXT.md](../CONTEXT.md) — Entidades
