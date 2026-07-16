---
type: source
source_kind: decisao
date:
entities: ["[[Cadencia]]", "[[PD Framework]]", "[[marketing]]", "[[produto]]"]
tags: [decisao, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.

# Decisões — produto-cadencia-frontend-memory

# Decisões — Sub-squad frontend Cadência

(append-only — mais recente em cima)

---

## 2026-06-19 — Guardrail de tenant + isolamento RLS (CAD-599 / CAD-594)

**Contexto:** todo o CRM usa `createAdminClient` (service_role) que BYPASSA RLS — o isolamento entre tenants depende do `.eq("tenant_id")` manual em cada query (risco #8). A sessão anterior subiu muita escrita multi-tenant nova.

**Decisão:**
- **Guard estático** (`tests/api/tenant-isolation-guard.test.ts`): `TENANT_SCOPED` passou a ser a lista autoritativa das **55 tabelas** com `tenant_id`+RLS (antes faltavam TODAS as do CRM). Toda rota nova que tocar tabela tenant-scoped sem sinal de escopo quebra no CI. É a proteção sempre-ligada. (+fix de path Windows; `unsubscribe` no ALLOW — escopa por token.)
- **Helper `tenant-guard.ts`** (CAD-599): `tenantInsert/Update/Delete` exigem `tenant_id`; `tenantInsert` valida `parent.tenant_id == tenant_id` (FK simples não pega — decisão Vitor: validar por código, não FK composta). Para os jobs service_role do CAD-577+ (scheduler/senders/seed/enriquecimento) adotarem — não retrofitei rotas já seguras.
- **Teste runtime RLS** (CAD-594, `tests/integration/rls-isolation.test.ts`): JWT real, A não vê/edita B. **SKIPA sem Supabase de teste** (vars `TEST_*`) — não toca produção. Seed de 2 tenants efêmeros fica como pré-requisito de quem rodar (evita seed em prod).
- `npm test` (vitest run) adicionado.

**Impacto:** proteção de isolamento agora coberta em CI pra todo o CRM. Em prod (só testes/helper, sem mudança de comportamento de runtime).

**Quem decidiu:** Felipe (priorizou blindar antes de Cadências) + helper por decisão Vitor (PRD §13 risco #8).

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-06-18 — Campos estruturados de contato: lead_source, is_icp, datas (CAD-616)

**Contexto:** "Trazer os 73 campos do GHL" — mas na prática só 52 keys existem em `contacts.custom_fields`. Avaliação campo-a-campo: ~16 manter no contato, ~14 mapear pra Empresa, ~22 descartar (press_*, stripe, score_ia, ecuro, cluster, e-mails internos). Felipe pediu ainda: `fonte_do_lead` como **select** com opções vastas, **is_icp** Sim/Não manual, e 4 datas (última compra / assinatura / vencimento de contrato / última interação).

**Decisão:**
- Esses campos viram **colunas estruturadas em `contacts`** (não `custom_field_defs` por-tenant) — porque "valem pra todos os users". Coluna existe pra todo tenant automaticamente.
- `lead_source` (select, opções em `LEAD_SOURCE_OPTS` no front — 23 fontes incl. Indicação/Referenciamento, Networking, Parceria, Revenda); `is_icp` ('Sim'/'Não'); 4 datas.
- **Backfill** best-effort: `lead_source` dos valores legados de `fonte_do_lead` (925); `is_icp` de `fit_icp` (Ideal→Sim, Fora→Não; 107). `custom_fields` legado **preservado** (opção conservadora — nada deletado).
- PATCH com allowlist de valor (lead_source ∈ opções, is_icp ∈ Sim/Não → 422) + `validDate` (data real).

**Impacto:** colunas na tabela + filtros + edição inline + board (lead_source/is_icp agrupáveis). Migration `20260619000000`. Os 🔴 (press/stripe/score_ia/ecuro/cluster/e-mails internos) NÃO migrados.

**Quem decidiu:** Felipe (aprovou baldes + opções + backfills) + review Claude Opus (2 P2 corrigidos).

---

## 2026-06-18 — Search global Ctrl+K (CAD-572)

**Contexto:** CRM próprio precisa de busca global estilo Linear/Notion. Plano previa `cmdk` + `search_vector` tsvector (CAD-561 §4.4), mas a generated column nunca foi criada e supabase-js não expõe `ts_rank_cd`.

**Decisão:**
- **Banco:** `search_vector` como `GENERATED ALWAYS AS (...) STORED` (sem trigger → sem drift, risco #3) + GIN + RPC `search_contacts` (ts_rank_cd). `REVOKE EXECUTE` de anon/authenticated + `GRANT` só service_role (defense-in-depth; RLS `contacts_owner` já isola por `tenant_id`).
- **UI:** `CommandPalette` **hand-rolled (sem `cmdk`)** — reusa padrão já existente no repo e evita dependência nova; montado global no `AppLayoutWrapper`. Critérios de aceite (Ctrl+K, <200ms, RLS, histórico) não dependem da lib.
- **Escopo V1 = só contatos.** Opportunities/notas/tasks entram quando essas entidades + seus `search_vector` existirem.

**Impacto:** Busca em produção (`master`). Endpoint `/api/app/search` via RPC. Palette antigo client-side (só nos carregados) removido.

**Quem decidiu:** Felipe (sequência do roadmap) + review Claude Opus headless (2 P1 corrigidos: REVOKE da RPC, `min(2)`/force-dynamic no endpoint).

---

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## 2026-05-25 — Bootstrap sub-squad frontend (PDL-237)

**Contexto:** Sub-squad aninhado criado durante bootstrap Squad pai Cadência (PDL-232).

**Decisão:** Pasta `frontend/` com CLAUDE.md + memory/STATE.md + decisions.md. Sem skills/workers próprios (compartilha com Squad pai). Cobertura: 5 áreas (`(app)`, `(admin)`, `(marketing)`, `(onboarding)`, `staff`) + 9 API routes + stack PWA + analytics múltiplos.

**Impacto:** Frontend tem identidade própria no PD Framework. Decisões técnicas frontend-only ficam aqui; decisões cross-stack vão pro Squad pai.

**Quem decidiu:** Felipe
