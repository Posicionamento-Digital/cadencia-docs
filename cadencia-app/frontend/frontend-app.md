> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/app/(app)/app/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/app/(app)/app/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# frontend-app — app autenticado (dashboard + features)

## TL;DR

Área autenticada do SaaS em `/app`. 14 rotas cobrindo dashboard, ideias, agenda, histórico, performance, fotos, créditos, planos, perfil, growth (wrappers GHL) e feedback.

## Identidade

- **Tipo:** Next.js 15 App Router (RSC + Client Components)
- **Stack:** React 19 + Tailwind + shadcn/ui + Serwist (PWA)
- **Path:** `src/app/(app)/app/`
- **Status:** ativo (Vercel, auto-deploy `master`)
- **Deps:** Supabase Auth, Workers Railway (geração), VPS (growth), GHL (wrappers)

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
| `/app/growth/calendario` | CalendarioClient | Social Planner GHL (iframe) |
| `/app/growth/contatos` | ContactsView | CRM GHL (smart_list, link externo) |
| `/app/growth/nutricao` | NutricaoClient | Nutrição de leads GHL (wrapper) |

## Componentes críticos

- `PipelineProgress` — indicador de progresso do pipeline de geração (polling `GET /api/app/generation-queue`)
- `AutoApprovePrompt` — toggle auto-approve de ideias
- `InstagramConnect` / `InstagramBanner` — conexão/reconexão conta Instagram
- `ProfileQuestionModal` — completa perfil progressivamente

## Growth wrappers (GHL)

Páginas de growth abrem GHL white-label: `${config.ghl.white_label_url}/v2/location/${locationId}/...`
- `white_label_url` de `tenant_config.config.ghl.white_label_url` (fallback: `https://app.msgsndr.com`)
- **GHL é motor invisível** — usuário nunca vê referências a GoHighLevel
- Score cards em Contatos: hardcoded "—" (G003 — não consultam banco)

## Don'ts

- Nunca expor "GoHighLevel" ou "GHL" na UI — sempre nome white-label
- `/app/preparing` só redireciona quando 5 ideias prontas — não alterar sem considerar UX de onboarding

---

## Quando usar

- Toda funcionalidade que exige tenant autenticado: gerar conteúdo, ver histórico, gerenciar planos, abrir CRM brancado.
- Adicionar nova feature de app — `/app/<nova>/page.tsx` + rota correspondente em `src/app/api/app/`.

## Quando NÃO usar

- ❌ Para páginas públicas (landing, pricing) — usar `(marketing)/`.
- ❌ Para fluxo onboarding incompleto (fases 1-3) — usar `(onboarding)/`.
- ❌ Para admin/super_admin — usar `app/admin/`.
- ❌ Componentes não-autenticados — RSC default exige session.

## Por que funciona assim

- [ADR-0003](../../../../docs/adr/0003-ghl-motor-invisivel.md) — GHL invisível. Wrappers `growth/*` abrem GHL white-label do tenant, sem expor a tech.
- App Router + RSC: server-side rendering por padrão; client components só onde precisa de interatividade.
- Serwist (PWA): app instalável + offline básico — diferencial para uso mobile.

## 🚫 Don'ts

- **Não** expor "GoHighLevel" ou "GHL" em copy, label ou screenshot. Usar "Cadencia Growth", "meus contatos".
- **Não** consultar dados de outro tenant — RLS deve filtrar; em service_role auditar.
- **Não** assumir que `tenant_config.config.ghl.white_label_url` sempre existe — fallback `https://app.msgsndr.com`.
- **Não** confiar nos score cards de Contatos (hardcoded "—" — G003).

## 🪦 Já tentamos

- **2026-04-15 — `confirm-client-side` perdia sessão** durante reload — bug de hidratação. Ver `2026-04-15_confirm-client-side-perdia-sessao.md`.
- **2026-05-15 — Ideias presas em "processing"** — UI mostrava spinner eterno. Ver `2026-05-15_ideias-presas-processing-spinner-eterno.md`.
- **2026-05-27 — Auth recovery token expirado update-password**: fluxo de recuperação senha quebrava. Ver `2026-05-27_auth-recovery-token-expirado-update-password.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Spinner eterno em /app/ideas | Job preso em `generation_queue` | Cleanup-stuck endpoint; ver workers |
| Página de growth abre URL `app.msgsndr.com` em vez de white-label | `white_label_url` não setado em `tenant_config` | Adicionar em `config.ghl.white_label_url` |
| Score cards Contatos mostram "—" | Comportamento esperado (G003) | UI hardcoded — não tem query |
| Build Vercel falha | TS strict + var não usada | Ver incident `vercel-build-var-nao-usada-haslinkedin` |

## 📚 Referências cruzadas

- [frontend-admin](admin/CLAUDE.md) — Sub-área super_admin
- [api-routes](../../../api/CLAUDE.md) — Endpoints consumidos
- [tracking-analytics](../../../../lib/analytics/CLAUDE.md) — Eventos
- [CONTEXT.md](../../../../../CONTEXT.md) — Tenant, GHL motor invisível
- [ADR-0003](../../../../../docs/adr/0003-ghl-motor-invisivel.md)
