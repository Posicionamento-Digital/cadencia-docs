---
date: 2026-05-25
tags: [documentacao, cadencia, sub-squad, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
sub_squad: frontend
type: source
entities: ["[[Cadencia]]", "[[comercial]]", "[[marketing]]"]
---
> 📍 Origem: `times/produto/cadencia/frontend/CLAUDE.md` no `pd-framework`. Última sync: 2026-05-25.

# Sub-squad frontend — Cadência

> Sub-squad aninhado dentro do Squad pai Cadência (`times/produto/cadencia/`). Criado em sessão guiada com Felipe (2026-05-25 — PDL-237).

---

## Escopo

Frontend Next.js 15 do produto Cadência. Cobre 5 áreas (route groups) + 9 API routes + stack PWA + analytics múltiplos.

**Repo:** `felipeluissalgueiro/cadencia-app` (parte `src/`).
**Deploy:** Vercel `main` push automático.

---

## Áreas (route groups)

| Área | Função |
|---|---|
| `(app)/` | App principal — UI do usuário cliente final (geração, aprovação Tinder, calendário, painel) |
| `(admin)/` | Admin interno (Felipe/equipe) — gestão de tenants, CRUD WhatsApp, planos, créditos |
| `(marketing)/` | Landing pages, copy comercial, páginas públicas marketing |
| `(onboarding)/` | Tour RPG 12 steps + provisioning automático (subconta GHL + blog Vercel + identity) |
| `staff/` | Área PD interna (acesso restrito a Felipe e PD) |

Outros paths:
- `conectar-whatsapp/` — fluxo OAuth WhatsApp (Stevo)

---

## API routes (`src/app/api/`)

| Route | Função |
|---|---|
| `app/` | Endpoints do app principal |
| `auth/` | Supabase Auth handlers (magic link, callback) |
| `capi/` | Meta CAPI tracking server-side |
| `growth/` | Endpoints expostos pra pipeline growth |
| `instagram/` | Instagram OAuth + publisher |
| `onboarding/` | Fluxo onboarding (provisioning) |
| `stevo/` | Integração WhatsApp Stevo (multi-tenant) |
| `v1/` | Endpoints versionados (legacy compat) |
| `webhooks/` | Webhooks externos (Stripe, GHL, Asaas legacy) |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | Next.js 15.5 (App Router) |
| UI | React 19.1 + Tailwind + shadcn/ui |
| PWA | Serwist (service worker) |
| Auth | Supabase Auth (magic link + senha) |
| State | React Query (`@tanstack/react-query`) |
| Forms | React Hook Form + Zod |
| Animations | Framer Motion |
| Markdown | react-markdown + remark-gfm |
| Icons | Lucide |
| Pagamento | Stripe SDK |
| Tracking | Mixpanel + PostHog + GA4 + GTM + Meta Pixel + UTM tracking |
| Errors | Sentry |
| Confetti | canvas-confetti |

---

## Lib relevante (`src/lib/`)

- `analytics.ts` — orquestra eventos cross-tracker
- `api.ts` — wrapper FastAPI workers
- `ghl.ts` + `ghl-oauth.ts` — integração GHL (motor invisível)
- `instagram.ts` — OAuth + publisher
- `meta-pixel.ts` — Meta Pixel browser
- `mixpanel.ts`, `posthog.ts` — analytics
- `plans.ts` — **fonte da verdade** dos planos Cadência
- `stripe.ts` — checkout Stripe
- `supabase/` — client browser + server
- `utm.ts` — UTM tracking unificado

---

## Workflows operacionais

- **Deploy:** push `main` → Vercel build automático
- **Preview:** PR abertos geram preview Vercel (bug PDL-69 — login redireciona prod)
- **Validação obrigatória pré-push:**
  - `npm run build` → zero erros (não-Sentry)
  - Lint OK
  - Build dev local rodado
  - Vercel ls Ready pós-push

---

## Pessoas

- **Felipe** — dev principal + Catarina (decisões de produto)
- **Time Dev cross-Time:** Vitor (arch), Amélia (dev), Sofia (UX), Camila (QA)
- **Luiz** — ciente, sem trabalho ativo (branches `luiz/pdl-11` a `pdl-19` são planejamento/inventário ainda não executado)

---

## Bloqueios

- PDL-25 P1 GHL OAuth nova agência (aguardando Felipe) — bloqueia onboarding novos tenants
- PDL-202 P1 subconta GHL onboarding (bug)
- PDL-18 acesso Luiz Railway+Vercel
- PDL-69 P3 preview Vercel login redirect

---

## PRs ativos hoje

- **#1** — Install Vercel Web Analytics (vercel/install-vercel-web-analytics)
- **#2** — fix(workers): suporte a OpenRouter via `OPENAI_BASE_URL/OPENAI_MODEL` (afeta workers, mas branch é no mesmo repo)

---

## Convenções

- **Branches:** `feat/pdl-XX-<desc>` (Felipe) ou `luiz/pdl-XX-<desc>` (Luiz)
- **Commits:** convencional (`feat(frontend): ...`, `fix(frontend): ...`)
- **Linguagem UI:** Tiazinha Véia — "seus posts", "suas ideias", "seu perfil". NUNCA "pipeline", "template", "dashboard", "deploy", "JSON" na UI visível ao usuário
- **GHL invisível:** UI não menciona "GoHighLevel" ou referencia subconta

---

## Foundation — consulta obrigatória

Antes de criar:
- Componente UI / feature visual → `../SOUL.md` § Identidade visual
- Feature nova de produto → `../foundation/product-vision.md` + `../foundation/multi-tenant-strategy.md`
- Mudança de copy → `../SOUL.md` § Voz/tom + `../foundation/target-customers.md` § Linguagem do cliente
- Decisão técnica arquitetural → `../foundation/tech-principles.md`

---

## Refs

- `memory/STATE.md` — estado atual
- `memory/decisions.md` — decisões específicas
- `../CLAUDE.md` — manual Squad pai
- `../SOUL.md` — identidade não-negociável
- Repo: `felipeluissalgueiro/cadencia-app/src/`
