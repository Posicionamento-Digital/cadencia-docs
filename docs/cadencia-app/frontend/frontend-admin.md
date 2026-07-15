> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/app/(app)/app/admin/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/app/(app)/app/admin/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# frontend-admin — painel administrativo

## TL;DR

Área super_admin em `/app/admin`. 14 sub-rotas cobrindo gestão de tenants, billing, custos LLM, roteamento de modelos, feature flags e impersonação.

## Identidade

- **Tipo:** Next.js 15 App Router
- **Path:** `src/app/(app)/app/admin/`
- **Status:** ativo
- **Deps:** Supabase (role `super_admin`), Workers Coolify VPS Master, VPS

## Rotas e funcionalidades

| Rota | Componente | Função |
|---|---|---|
| `/app/admin/dashboard` | AdminDashboard | Overview: tenants, planos ativos, posts totais |
| `/app/admin/tenants` | TenantsTable | CRUD tenants + status ativo/suspenso |
| `/app/admin/users` | UsersTable | CRUD usuários |
| `/app/admin/billing` | BillingTable | Cobranças e planos |
| `/app/admin/billing/credits` | CreditsTable | Créditos manuais por tenant |
| `/app/admin/content` | ContentTable | Conteúdo global |
| `/app/admin/editorials` | EditorialsTable | Editoriais por tenant |
| `/app/admin/logs` | LogsTable | Audit logs |
| `/app/admin/costs` | CostsDashboard + ApiCallLogsTab | Custos de chamadas LLM por tenant |
| `/app/admin/models` | ModelRouterTable + AgentPromptsTab | Roteamento de modelos LLM + prompts |
| `/app/admin/metrics` | MetricsView | Métricas agregadas |
| `/app/admin/flags` | FlagsView | Feature flags globais (5 flags) |
| `/app/admin/onboarding` | OnboardingTable | Estado de onboarding por tenant |
| `/app/admin/impersonate` | ImpersonateView | Impersonar tenant (super_admin only) |
| `/app/admin/tickets` | TicketsTable | Suporte/tickets |

## Feature flags globais

| Flag | Default | Função |
|---|---|---|
| `maintenance_mode` | false | Desativa app para manutenção |
| `auto_approve_default` | false | Auto-aprova ideias sem review |
| `multi_version_default` | false | Gera 3 versões por padrão |
| `new_carousel_models` | false | Habilita novos modelos de carrossel |
| `chat_ideas` | false | Liga/desliga chat "Tenho uma Ideia" |

## CostsDashboard

Rastreia todas as chamadas LLM por tenant (tabela `api_call_logs`). Permite identificar tenants de alto custo e otimizar modelo routing.

## ModelRouter

Configura qual LLM usar por tipo de conteúdo e por tenant. Overrides de prompt por agente. API: `POST /api/app/admin/model-routing` + `POST /api/app/admin/agent-prompts`.

## Don'ts

- Acesso `super_admin` verificado no backend — nunca confiar em check só no frontend
- Export CSV (`GET /api/app/admin/export`) tem dados sensíveis — não expor publicamente

---

## Quando usar

- Operação interna PD: gerenciar tenants, monitorar custos LLM, configurar model routing, toggle feature flags globais, impersonar tenant para suporte.

## Quando NÃO usar

- ❌ Por usuários tenant — role `super_admin` obrigatório, RLS bloqueia.
- ❌ Para exportar dados de outro tenant para uso externo — auditoria + LGPD.
- ❌ Sem 2FA habilitado (boa prática, ainda que técnico não exija hoje).

## Por que funciona assim

- Custos LLM agregados em `api_call_logs` — visibilidade granular por tenant para otimizar prompts/modelos.
- Model routing configurável por tenant — permite testar Opus vs Sonnet sem deploy.
- Impersonate: sessão temporária mascarada como o tenant para diagnosticar sem login do usuário.

## 🚫 Don'ts

- **Não** alterar `maintenance_mode=true` sem avisar Felipe — quebra app de todos os tenants.
- **Não** sair de uma sessão impersonate sem logar audit log explícito.
- **Não** dar créditos manuais sem registro em `billing/credits` audit.
- **Não** mudar feature flag global em produção sem testar staging.

## 🪦 Já tentamos

- Feature flag rollout sem staging → bug em produção visível para todos. Razão de manter `maintenance_mode` como gate.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| 403 ao acessar /app/admin | Sem role super_admin | Adicionar em `user_tenant_roles` |
| Custos LLM 0 para tenant ativo | `api_call_logs` sem registro | Verificar logging nos workers |
| Impersonate não sai limpa | Sessão duplicada | Logout completo + clear cookies |
| Model routing não aplica | Cache no worker | Reiniciar worker / invalidar cache |

## 📚 Referências cruzadas

- [frontend-app](../CLAUDE.md) — App tenant
- [api-routes](../../../../api/CLAUDE.md) — Endpoints `/api/app/admin/*`
- [supabase-schema](../../../../../supabase/CLAUDE.md) — Tabelas `api_call_logs`, `audit_logs`
