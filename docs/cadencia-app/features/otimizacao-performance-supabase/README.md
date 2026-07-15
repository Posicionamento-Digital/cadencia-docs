> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/features/otimizacao-performance-supabase/README.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/features/otimizacao-performance-supabase/README.md)
> Sincronizado via `sync_cadencia_docs.py` em 2026-05-29 (PDL-342).

---

# Otimização de Performance Supabase — Cadência

> Conjunto de mudanças que reduziu ~75% do consumo de CPU do banco e melhorou latência geral do app. Aplicado em 2026-05-19.

## TL;DR

Dashboard do Supabase reportava "Your project is currently exhausting multiple resources". Diagnóstico via `pg_stat_statements` mostrou ~75% do tempo de CPU consumido pelo decoder de WAL do Realtime, mais RLS policies executando `auth.jwt()` por linha. Sete mudanças (PDL-160 a PDL-166) atacaram as causas — frontend deixou de usar Realtime e passou a fazer polling sob demanda, RLS policies foram envolvidas em subselect, indexes não usados foram removidos.

| Antes | Depois (esperado, validar em 24h via PDL-162) |
|---|---|
| ~75% CPU em `SELECT wal->>...` (decoder Realtime) | Decoder idle (publication vazia) |
| `auth.jwt()` executado por linha em RLS | `(SELECT auth.jwt())` vira initPlan, executa 1x |
| 24.131 seq_scan em `user_tenant_roles` | Partial index `idx_user_tenant_roles_super_admin` |
| 15 indexes não usados (~3.4 MB) | 9 dropados, 6 mantidos (uso confirmado em código) |
| `idle_in_transaction_session_timeout = 0` | `5min` (conexões zumbis matadas) |
| Subscription Realtime sempre ativa no dashboard | Polling 3s só enquanto há job ativo |

## Contexto

Instância Cadência (`elefbabxkaigusjiiflu`) é **Compute Micro** (1 GB RAM, 2 vCPU shared, 87 MB/s baseline IO, 60 conexões diretas) na org `Posicionamento Digital` em plano **Pro**. Dashboard começou a sinalizar exaustão de recursos com app travando e Felipe reportando lentidão geral.

Antes de assumir que era falta de hardware (upgrade pra Small = +US$15/mês), investigação via Management API revelou que o problema era 100% de **uso ineficiente** — Micro aguentava de sobra com as queries otimizadas.

## Diagnóstico

### Top 2 queries consumindo CPU (via `pg_stat_statements`)

| % do tempo total | Query | Causa |
|---|---|---|
| **46.6%** | `SELECT wal->>... as type, schema, table...` (888k calls) | Decoder de WAL do Realtime processando a publication inteira |
| **28.3%** | mesma query (453k calls) | idem |

Combinados: **~75% da CPU do DB** consumido pelo Realtime.

### Tabela mais escrita (alimentando o WAL)

| Tabela | Writes (24h) |
|---|---|
| scoring_events | 11.508 |
| pipeline_status | 3.646 |
| content_documents | 2.999 |
| api_call_logs | 2.112 |
| content_ideas | 1.881 |
| generation_queue | 1.557 |

Mesmo que só `pipeline_status` estivesse na publication `supabase_realtime`, o **decoder processa o WAL inteiro** (todas as tabelas) e filtra depois pela publication.

### RLS policies não-otimizadas

`pg_policies` mostrou 116 policies em `public.*` chamando `auth.jwt() ->> 'tenant_id'`, `auth.uid()` ou `auth.role()` diretamente. Pegadinha clássica documentada pela Supabase: essas funções são `STABLE` mas o planner não cacheia entre linhas — em queries que retornam N linhas, são chamadas N vezes.

`user_tenant_roles` acumulou **24.131 seq_scans** pra apenas 15 linhas. `tenants`: 7.013 scans.

## Solução — 7 sub-issues

| PDL | Tipo | Esforço | Status |
|---|---|---|---|
| [PDL-159](https://linear.app/posicionamento-digital/issue/PDL-159) | Parent — Otimização performance Supabase | — | In Progress (aguarda PDL-162) |
| [PDL-160](https://linear.app/posicionamento-digital/issue/PDL-160) | Migration SQL — Drop publication `supabase_realtime` | XS | ✅ Done |
| [PDL-161](https://linear.app/posicionamento-digital/issue/PDL-161) | Refactor TS — Polling on-demand em vez de Realtime | S | ✅ Done |
| [PDL-162](https://linear.app/posicionamento-digital/issue/PDL-162) | Operacional — Validar economia 24h pós-deploy | — | 🔄 In Progress |
| [PDL-163](https://linear.app/posicionamento-digital/issue/PDL-163) | Migration SQL — RLS subselect + index super_admin | M | ✅ Done |
| [PDL-164](https://linear.app/posicionamento-digital/issue/PDL-164) | Investigação — Schema reloads excessivos PostgREST | XS | ✅ Done |
| [PDL-165](https://linear.app/posicionamento-digital/issue/PDL-165) | Migration SQL — Drop 9 indexes não usados | S | ✅ Done |
| [PDL-166](https://linear.app/posicionamento-digital/issue/PDL-166) | DB config — `idle_in_transaction_session_timeout=5min` | XS | ✅ Done |

## Mudanças aplicadas

### PDL-160 — Drop publication

```sql
ALTER PUBLICATION supabase_realtime DROP TABLE public.pipeline_status;
```

- Migration: `supabase/migrations/20260519180000_drop_realtime_publication.sql`
- Resultado: `pg_publication_tables WHERE pubname='supabase_realtime'` retorna 0 linhas
- Decoder de WAL fica idle quando não há tabelas publicadas

### PDL-161 — Polling on-demand

- Arquivo principal: `src/hooks/usePipelineStatus.ts`
- Subscriptions Realtime removidas (eram em `generation_queue` + `pipeline_status`)
- Substituídas por `setInterval(fetchJobs, 3000)` ativado só quando `hasActiveJobs === true`
- `useRef` espelha função para evitar closure stale dentro do interval
- Listener `window.addEventListener('pipeline:job-created', ...)` permite refetch sob demanda quando outra parte do app cria um job

Dispatch do evento em 4 pontos do app:
- `src/app/(app)/app/ideas/page.tsx:254` — swipe direita simples (após `workersApi('/pipeline/run').then()`)
- `src/app/(app)/app/ideas/page.tsx:319` — `confirmApprove` no fluxo multi-canal
- `src/app/(app)/app/ideas/page.tsx:332` — `.then()` do fetch `/api/app/generation-queue` (canais Growth)
- `src/components/ideas/IdeasSwipe.tsx:52` — `handleSwipe`

**Race condition corrigida durante review:** o agent inicial colocou o dispatch síncrono **antes** do `.then()` da chamada ao worker. Como o worker faz INSERT em `generation_queue` antes de retornar (ver `cadencia-workers/src/api/routes/pipeline.py:85`), o dispatch precisa esperar a Promise resolver — senão o fetch dispara, acha 0 jobs, polling não inicia. Corrigido em commit `928857e` movendo dispatch para `.then()`.

### PDL-163 — RLS subselect

- Migration 1: `supabase/migrations/20260519170000_optimize_rls_policies.sql` — 116 policies em `BEGIN/COMMIT`, cada uma envolve `auth.jwt()`/`uid()`/`role()` em `(SELECT ...)`
- Migration 2: `supabase/migrations/20260519170001_create_super_admin_index.sql` — `CREATE INDEX CONCURRENTLY idx_user_tenant_roles_super_admin ON user_tenant_roles(user_id) WHERE is_super_admin = true` (partial, fora de txn)

Tabelas tocadas (31): tenants, users, user_tenant_roles, tenant_onboarding, tenant_dossier, tenant_visual_identity, tenant_editorials, tenant_config, content_ideas, research_documents, content_headlines, content_documents, generation_queue, pipeline_status, tenant_plans, credit_transactions, profile_responses, tenant_profile, audit_logs, publish_attempts, publish_jobs, tenant_themes, chat_sessions, tenant_memories, support_tickets, social_connections, content_feedback, published_posts, carousel_models, carousel_selection_rules, cost_config, asaas_webhook_log, feature_flags, model_routing, style_configs.

**Bug pré-existente corrigido na hora:** a migration original do agent referenciava tabela inexistente `tenant_users` (deveria ser `user_tenant_roles`) em 2 policies copiadas literalmente de uma migration órfã. Corrigido em commit `e70dbec` substituindo pelo `published_posts_tenant_isolation` real do banco.

### PDL-165 — Drop indexes

- Migration: `supabase/migrations/20260519170002_drop_unused_indexes.sql`

| Index | Decisão | Justificativa |
|---|---|---|
| idx_research_documents_topic_cluster | DROP | 0 scans, sem feature relacionada |
| idx_research_documents_nicho | DROP | idem |
| idx_research_documents_editorial_function | DROP | idem |
| idx_tenant_themes_tenant_id | DROP | redundante com composite `(tenant_id, version DESC)` |
| idx_api_call_logs_task | DROP | 0 scans |
| idx_audit_logs_target | DROP | 0 scans |
| idx_support_tickets_type | DROP | 0 scans |
| idx_chat_sessions_tenant_id | DROP | queries usam `.eq("id", pk)`; composite cobre listagens |
| idx_stripe_webhook_log_processed | DROP | webhook filtra só por event_id (unique) |
| idx_document_chunks_embedding | MANTER | RAG ativo (`cadencia-workers/src/workers/rag.py`) |
| idx_tenant_memories_embedding | MANTER | chat agent usa `get_relevant_memories` |
| idx_tenant_plans_stripe_sub | MANTER | webhook stripe usa em `.eq("stripe_subscription_id", sub.id)` |
| idx_audit_logs_created | MANTER | `/admin/logs` faz `ORDER BY created_at DESC LIMIT 200` |
| idx_support_tickets_created | MANTER | admin dashboard idem |
| idx_cleanup_pending | MANTER | conservador — cron externo possível |

Cada DROP traz comentário com a definição original em `-- ROLLBACK: CREATE INDEX ...` para recuperação rápida.

### PDL-166 — idle_in_transaction_session_timeout

```sql
ALTER DATABASE postgres SET idle_in_transaction_session_timeout = '5min';
```

Aplicado direto via Management API (não precisa restart). Confirmado em `pg_db_role_setting`. Sem migration versionada (config de DB, não schema).

### PDL-164 — Schema reload investigation (resolvido sem código)

`SELECT pg_catalog.obj_description($1::regnamespace, $2)` consumia 23.2% do tempo total — PostgREST recarregando schema cache. Causa raiz: event triggers built-in do PostgREST (`pgrst_drop_watch`, `pgrst_ddl_watch`) disparando `NOTIFY pgrst` em qualquer DDL.

A DDL frequente vinha do **Supabase Realtime** fazendo ALTER PUBLICATION internamente. Como PDL-160 dropou a publication, o trigger ficou idle. Issue fechada sem código novo.

## Commits no master

```
3a144c2 feat(db): drop pipeline_status from supabase_realtime publication
e70dbec fix(db): substituir referencias a tabela inexistente tenant_users
946e0b7 Merge feat/pdl-161-polling-on-demand
9b3faa8 Merge feat/pdl-163-rls-subselect
a41620e Merge feat/pdl-165-drop-unused-indexes
928857e fix(pipeline): mover dispatch pipeline:job-created para .then() — corrige race condition
67b13a7 feat(db): otimizar RLS policies com subselect auth.jwt() — Closes PDL-163
2c214e6 feat(db): drop indexes não usados — Closes PDL-165
```

## Validação

### DB-side (em 2026-05-19 ~19:25 UTC)

- Job de teste `995095e1-8e93-400e-8360-c36812d79ed9` (tenant felipeluissalgueiro)
- Aprovação → job criado no mesmo segundo (race condition resolvida)
- Pipeline completou em 1m13s, 7/7 steps
- Estado final coerente: idea `used`, job `completed`

### UI-side (confirmado por Felipe)

- Spinner apareceu, atualizou progresso, sumiu sozinho quando completou
- App reportado como "mais rápido como um todo" — efeito esperado da PDL-163 (queries autenticadas executando `auth.jwt()` 1x por query)

### Validação empírica (PDL-162, em curso)

`pg_stat_statements_reset()` rodado às 2026-05-19 18:03:17 UTC. Coleta agendada pra 2026-05-20 ~18h. Métricas esperadas:

- `SELECT wal->>...` NÃO aparece mais no top-15
- `mean_exec_time` de queries `pgrst_source` reduzido em ≥30%
- `obj_description` abaixo de 5% do tempo total
- Aviso "exhausting multiple resources" sumiu do dashboard

## 🚫 Don'ts

- **Não recriar a publication `supabase_realtime` pra outra tabela sem rediscutir** — todo write nas tabelas publicadas vira CPU no decoder. Se feature nova precisar de Realtime, considerar primeiro se polling sob demanda resolve.
- **Não escrever policies RLS com `auth.jwt()`/`uid()`/`role()` direto na qual** — sempre envolver em `(SELECT ...)`. Padrão estabelecido.
- **Não fazer dispatch de evento DOM antes de Promise resolver** — race condition silenciosa. Usar `.then()`.
- **Não usar `.catch(() => {})` em chamadas críticas de pipeline** — engole erros, gera bugs órfãos (caso PDL-167/168 documentando o sintoma de idea presa em `approved`).
- **Não dropar index sem grep no código** — verificar uso real, manter rollback comentado na migration.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Spinner não aparece após aprovar idea | Dispatch antes do INSERT (race) | Verificar que `dispatchEvent('pipeline:job-created')` está em `.then()` do worker call |
| Spinner trava indefinidamente | Polling não para; closure stale | Verificar `useRef` espelhando função e `cancelled` flag no cleanup |
| CPU alta sem motivo aparente | Alguma publication ativa | `SELECT * FROM pg_publication_tables;` deve retornar lista vazia |
| Query autenticada lenta em tabela grande | Policy RLS com `auth.jwt()` sem subselect | `SELECT * FROM pg_policies WHERE qual ILIKE '%auth.jwt()%' AND qual NOT ILIKE '%SELECT auth.jwt%'` deve retornar 0 |
| Conexão zumbi segurando slot | Transação esquecida | `SHOW idle_in_transaction_session_timeout;` deve ser `5min`, não `0` |

## 🪦 Pegadinhas encontradas durante execução

- **CONCURRENTLY exige fora de transação.** Migration auto-wrap do Supabase quebra. Separar em arquivo próprio sem BEGIN/COMMIT.
- **Migration referencia tabela `tenant_users` (inexistente)** em 2 policies originais do projeto. Pré-existente. Corrigido na hora, mas indica que migrations órfãs entraram em prod sem validação.
- **Race condition no dispatch DOM** é difícil de pegar em review estática — só aparece em teste E2E quando o worker é lento (cold start do worker).
- **1Password CLI tem timeout de sessão.** Mid-execução, comandos `op` começaram a falhar com `authorization timeout`. Felipe precisou reautenticar localmente.

## Próximos passos (issues abertas)

| PDL | Resumo |
|---|---|
| [PDL-167](https://linear.app/posicionamento-digital/issue/PDL-167) | Guardrail: cron pra limpar ideas órfãs em `approved` sem job |
| [PDL-168](https://linear.app/posicionamento-digital/issue/PDL-168) | Fix definitivo: endpoint atômico `POST /ideas/:id/approve` (elimina race entre PATCH e POST `/pipeline/run`) |
| [PDL-169](https://linear.app/posicionamento-digital/issue/PDL-169) | Bugs encontrados em `/app/ideas`: RPC `debit_credits` ignora `grace`, React #418, 500 generation-queue, SW error |

## Referências

- Doc Supabase Realtime overhead: https://supabase.com/docs/guides/realtime/postgres-changes#scalability
- Doc RLS performance: https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices
- Hub de Incidentes (geral): `Hub Projetos/Incidentes/INDEX.md`
