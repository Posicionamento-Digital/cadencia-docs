# frontend-app — app autenticado (dashboard + features)

## TL;DR

Área autenticada do SaaS em `/app`. Rotas cobrem dashboard, ideias, agenda, histórico, performance, fotos, créditos, perfil, CRM, nutrição e feedback.

## Identidade

- **Tipo:** Next.js 15 App Router (RSC + Client Components)
- **Stack:** React 19 + Tailwind + shadcn/ui + Serwist (PWA)
- **Path:** `src/app/(app)/app/`
- **Status:** ativo (Vercel, auto-deploy `master`)
- **Deps:** Supabase Auth, CRM Cadência, Workers Coolify VPS Master e VPS growth

## Rotas principais

| Rota | Componente | Função |
|---|---|---|
| `/app` | HomeDashboard | Dashboard principal com fila de geração |
| `/app/ideas` | IdeasView | Lista + aprovação de ideias via chat |
| `/app/schedule` | ScheduleView | Calendário de posts |
| `/app/history` | HistoryView | Histórico de conteúdo gerado |
| `/app/performance` | PerformanceDashboard | Métricas Instagram |
| `/app/photos` | PhotosView | Banco de fotos do tenant |
| `/app/credits` | CreditsView | Créditos e consumo |
| `/app/plans` | PlansView | Planos + checkout Stripe |
| `/app/plans/callback` | — | Pós-checkout Stripe |
| `/app/profile` | ProfileView | Perfil e configurações |
| `/app/feedback/[id]` | FeedbackView | Feedback por conteúdo |
| `/app/preparing` | PreparingView | Polling pós-onboarding (aguarda 5 ideias) |
| `/app/growth/calendario` | CalendarioClient | Calendário de conteúdo e entregas |
| `/app/growth/contatos` | ContactsView | Contatos do CRM Cadência |
| `/app/growth/nutricao` | NutricaoClient | Nutrição baseada em score/eventos do CRM |

## Componentes críticos

- `PipelineProgress` — indicador de progresso do pipeline de geração (polling `GET /api/app/generation-queue`)
- `AutoApprovePrompt` — toggle auto-approve de ideias
- `InstagramConnect` / `InstagramBanner` — conexão/reconexão conta Instagram
- `ProfileQuestionModal` — completa perfil progressivamente

## CRM e Growth nativos

Contatos, empresas, oportunidades, pipelines, tags, campos, score e temperatura
vêm do CRM Cadência. Toda consulta e mutação deve resolver o tenant antes de
acessar o Supabase.

## Don'ts

- `/app/preparing` só redireciona quando 5 ideias prontas — não alterar sem considerar UX de onboarding

---

## Quando usar

- Toda funcionalidade que exige tenant autenticado: gerar conteúdo, ver histórico, gerenciar créditos e operar o CRM.
- Adicionar nova feature de app — `/app/<nova>/page.tsx` + rota correspondente em `src/app/api/app/`.

## Quando NÃO usar

- ❌ Para páginas públicas (landing, pricing) — usar `(marketing)/`.
- ❌ Para fluxo onboarding incompleto (fases 1-3) — usar `(onboarding)/`.
- ❌ Para admin/super_admin — usar `app/admin/`.
- ❌ Componentes não-autenticados — RSC default exige session.

## Por que funciona assim

- App Router + RSC: server-side rendering por padrão; client components só onde precisa de interatividade.
- Serwist (PWA): app instalável + offline básico — diferencial para uso mobile.

## 🚫 Don'ts

- **Não** consultar dados de outro tenant — RLS deve filtrar; em service_role auditar.

## 🪦 Já tentamos

- **2026-04-15 — `confirm-client-side` perdia sessão** durante reload — bug de hidratação. Ver `2026-04-15_confirm-client-side-perdia-sessao.md`.
- **2026-05-15 — Ideias presas em "processing"** — UI mostrava spinner eterno. Ver `2026-05-15_ideias-presas-processing-spinner-eterno.md`.
- **2026-05-27 — Auth recovery token expirado update-password**: fluxo de recuperação senha quebrava. Ver `2026-05-27_auth-recovery-token-expirado-update-password.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Spinner eterno em /app/ideas | Job preso em `generation_queue` | Cleanup-stuck endpoint; ver workers |
| CRM retorna vazio | tenant ou filtros incorretos | validar `resolveTenant()` e `tenant_id` |
| Build Vercel falha | TS strict + var não usada | Ver incident `vercel-build-var-nao-usada-haslinkedin` |

## 📚 Referências cruzadas

- [frontend-admin](admin/CLAUDE.md) — Sub-área super_admin
- [api-routes](../../../api/CLAUDE.md) — Endpoints consumidos
- [tracking-analytics](../../../../lib/analytics/CLAUDE.md) — Eventos
- [CONTEXT.md](../../../../../CONTEXT.md) — linguagem do domínio
