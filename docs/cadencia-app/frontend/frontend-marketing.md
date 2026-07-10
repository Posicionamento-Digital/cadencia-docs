> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/app/(marketing)/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/app/(marketing)/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# frontend-marketing — landing pages e marketing

## TL;DR

Páginas públicas de marketing (landing page, pricing, etc.) e conectar-whatsapp. Deploy no Vercel, sem autenticação.

## Identidade

- **Tipo:** Next.js 15 App Router (RSC)
- **Paths:**
  - `src/app/(marketing)/` — landing, pricing, etc.
  - `src/app/conectar-whatsapp/` — página pública de QR Stevo
- **Status:** ativo
- **Deps:** Stripe (pricing page), Supabase (planos), Stevo (QR page)

## conectar-whatsapp

Página pública (sem auth) para o cliente escanear QR code do WhatsApp via Stevo:
- Polling de status a cada 3s (`GET /api/stevo/status`)
- Renovação de QR a cada 20s (`POST /api/stevo/qr`)
- NÃO requer sessão Supabase — acessível via link externo

## Don'ts

- GHL não deve aparecer em nenhuma página de marketing
- `conectar-whatsapp` é pública — não expor informações sensíveis de tenant

---

## Quando usar

- Landing pages públicas, pricing, blog institucional.
- `/conectar-whatsapp` para clientes que entram via link direto Stevo QR.

## Quando NÃO usar

- ❌ Para qualquer conteúdo que exige autenticação — usar `(app)/app/`.
- ❌ Para conteúdo dinâmico por tenant — landing não conhece o tenant.
- ❌ Expor "GoHighLevel" — [ADR-0003](../../../docs/adr/0003-ghl-motor-invisivel.md).

## Por que funciona assim

- RSC default — SEO + performance.
- `conectar-whatsapp` pública porque cliente pode receber QR antes de criar conta.

## 🚫 Don'ts

- **Não** referenciar GHL, GoHighLevel, MsgSndr em qualquer copy.
- **Não** expor info sensível de tenants em `/conectar-whatsapp` (página é pública).
- **Não** usar client-side data fetching para pricing — Stripe é fonte da verdade, render server-side.

## 🪦 Já tentamos

- Landing com referência a GHL → cliente perguntou "vou pagar por outra ferramenta?". Razão do ADR-0003.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Stevo QR não atualiza | Polling parou; sessão Stevo caiu | Reiniciar polling; reconectar Stevo |
| Pricing desatualizado | Cache RSC stale | `revalidate` curto + ISR |
| SEO ruim | Faltam meta tags por página | Adicionar `generateMetadata` em cada page.tsx |

## 📚 Referências cruzadas

- [api-integrations](../../api/webhooks/CLAUDE.md) — `/api/stevo/*`
- [payment-billing](../../api/app/billing/CLAUDE.md) — Stripe pricing
- [ADR-0003](../../../../docs/adr/0003-ghl-motor-invisivel.md)
