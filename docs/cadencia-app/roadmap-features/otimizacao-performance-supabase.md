---
date: 2026-05-19
tags: [documentacao, feature, cadencia, supabase, performance]
moc: "[[MOC-Projetos]]"
status: aplicado
pdls: [PDL-159, PDL-160, PDL-161, PDL-162, PDL-163, PDL-164, PDL-165, PDL-166]
type: source
entities: ["[[Cadencia]]"]
---
# Otimização de Performance Supabase — Cadência

> Conjunto de mudanças que reduziu ~75% do consumo de CPU do banco e melhorou latência geral do app. Aplicado em 2026-05-19.

## Identidade

- **Tipo:** feature transversal (DB + frontend + worker)
- **Stack:** PostgreSQL 17 (Supabase) + Next.js 15 + React 19
- **Path no repo:** `docs/features/otimizacao-performance-supabase/`
- **Status:** aplicado em produção, aguarda validação 24h (PDL-162)

## O que é

Pacote de 7 sub-issues (PDL-160 a PDL-166) sob a parent PDL-159, atacando esgotamento de recursos da instância Supabase Compute Micro (1 GB RAM, 2 vCPU shared) do Cadência.

## Para que serve

Manter Cadência rodando na instância **Micro** (sem upgrade pra Small = US$15/mês a mais) com folga de performance pra crescer. Eliminar lentidão geral percebida pelo usuário.

## Como funciona — 7 frentes

| PDL | O que faz |
|---|---|
| PDL-160 | Drop `pipeline_status` da publication `supabase_realtime` (mata decoder de WAL idle) |
| PDL-161 | Refactor `usePipelineStatus.ts` pra polling 3s sob demanda (substitui subscriptions Realtime) |
| PDL-162 | Validação empírica 24h após deploy via `pg_stat_statements_reset()` |
| PDL-163 | 116 policies RLS reescritas com `(SELECT auth.jwt())` em vez de `auth.jwt()` direto + partial index pra super_admin |
| PDL-164 | Investigação concluída — schema reloads vinham do Realtime, resolveu indiretamente via PDL-160 |
| PDL-165 | Drop de 9 indexes não usados (mantidos 6 com uso confirmado em código) |
| PDL-166 | `ALTER DATABASE` setando `idle_in_transaction_session_timeout=5min` |

## Quickstart — diagnosticar instância Supabase

Via Management API (PAT em 1P `Supabase - ClaudeCode - CLI` vault `databases`):

```sql
-- Top queries consumindo CPU
SELECT calls, round(total_exec_time::numeric,0) AS total_ms,
       round((100*total_exec_time/sum(total_exec_time) over ())::numeric,1) AS pct,
       left(query, 120) AS q
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 15;

-- Policies RLS não-otimizadas
SELECT tablename, policyname, qual
FROM pg_policies
WHERE schemaname='public'
  AND (qual ILIKE '%auth.jwt()%' OR qual ILIKE '%auth.uid()%')
  AND qual NOT ILIKE '%SELECT auth.%';

-- Publication Realtime ativa
SELECT * FROM pg_publication_tables WHERE pubname='supabase_realtime';

-- Indexes não usados
SELECT relname AS tabela, indexrelname AS idx, idx_scan
FROM pg_stat_user_indexes WHERE schemaname='public' AND idx_scan < 10
ORDER BY pg_relation_size(indexrelid) DESC LIMIT 20;
```

## Decisões (ADRs)

- Manter instância **Micro** — Pro tem 8 GB DB e 100 GB Storage incluídos; problema era 100% uso ineficiente, não falta de hardware
- Substituir Realtime por polling sob demanda — Realtime tem custo fixo (decoder WAL), polling tem custo proporcional ao uso
- Wrap `auth.jwt()` em subselect — padrão oficial Supabase ([doc](https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices))
- Manter pgvector indexes — RAG ativo em `cadencia-workers/src/workers/rag.py`

## 🚫 Don'ts

- **Não recriar `supabase_realtime` publication sem rediscutir** — todo write nas tabelas publicadas vira CPU no decoder
- **Não escrever policies RLS com `auth.jwt()`/`uid()`/`role()` direto na qual** — sempre `(SELECT ...)`
- **Não usar `.catch(() => {})` em chamadas críticas** — engole erros, gera bugs órfãos
- **Não dropar index sem grep no código** — verificar uso real

## 🔥 Troubleshooting

| Sintoma | Causa | Fix |
|---|---|---|
| CPU alta inexplicável | Publication com tabela de alto write | `SELECT * FROM pg_publication_tables WHERE pubname='supabase_realtime'` deve estar vazio |
| Query autenticada lenta | RLS sem subselect | Grep `pg_policies` por `auth.jwt()` sem `(SELECT ...)` |
| Spinner trava | Closure stale no setInterval | Usar `useRef` espelhando função |
| Conexão zumbi | Transação esquecida | `SHOW idle_in_transaction_session_timeout;` deve ser `5min` |

## Histórico

- 2026-05-19 — Aplicado em produção. 7 PDLs Done (160, 161, 163, 164, 165, 166), PDL-162 aguardando 24h. Commits: 3a144c2, e70dbec, 946e0b7, 9b3faa8, a41620e, 928857e, 67b13a7, 2c214e6.

## Pegadinhas encontradas

- **Migration referenciando `tenant_users` (tabela inexistente)** em 2 policies originais — pré-existente, corrigido na hora
- **Race condition no dispatch DOM** — dispatch precisa ir no `.then()` da Promise, não síncrono
- **CONCURRENTLY exige fora de transação** — migration auto-wrap quebra, separar em arquivo próprio
- **1Password CLI timeout** mid-sessão — Felipe precisou reautenticar localmente

## Notas Relacionadas

- [[Projetos/cadencia-roadmap/Docs/chat-tenho-uma-ideia]]
- [[Projetos/cadencia-roadmap/Docs/billing-stripe-ghl]]

## Bugs colaterais descobertos (issues abertas)

- **[PDL-167](https://linear.app/posicionamento-digital/issue/PDL-167)** — Cron pra limpar ideas órfãs em `approved` sem job (guardrail)
- **[PDL-168](https://linear.app/posicionamento-digital/issue/PDL-168)** — Endpoint atômico `POST /ideas/:id/approve` (elimina race PATCH+POST)
- **[PDL-169](https://linear.app/posicionamento-digital/issue/PDL-169)** — RPC `debit_credits` ignora status `grace` + bugs UI
- **[PDL-170](https://linear.app/posicionamento-digital/issue/PDL-170)** — Feature "Tenho uma Ideia": título cru, slug ruim, email não disparado
