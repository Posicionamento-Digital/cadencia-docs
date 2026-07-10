> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/tracking-stack.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/tracking-stack.md)
> Sincronizado via `sync_cadencia_docs.py` em 2026-05-29 (PDL-342).

---

# Tracking Stack — Cadencia

Sistema completo de rastreamento de conversões e atribuição. Cobre browser pixel, CAPI server-side e UTMs.

---

## Visão Geral

```
Usuário acessa a LP
      │
      ▼
[UtmCapture.tsx]           ← captura UTMs/referrer, salva em sessionStorage + localStorage + cookie
      │
      ▼
Usuário se cadastra
      │
      ├─► [sign-up-form.tsx]     → lê attribution do storage → envia no POST /api/auth/provision-tenant
      │         │
      │         ▼
      │   [provision-tenant]     → salva em tenant_config.config.attribution (Supabase)
      │
      ├─► [meta-pixel.ts fbq()]  → evento Lead no browser (Meta Pixel 159019099458057)
      │
      └─► [meta-pixel.ts CAPI]   → POST /api/capi → Meta Graph API v21.0 (server-side)
```

---

## Componentes

### 1. `src/lib/utm.ts`

Captura UTMs e inferência de canal para tráfego orgânico.

```typescript
import { getAttribution, getSessionUtm, getFirstTouchUtm } from "@/lib/utm";

// Lê atribuição completa para enviar no cadastro
const attribution = getAttribution();
// { first_touch: UtmData, last_touch: UtmData }

// Estrutura UtmData:
// {
//   utm_source, utm_medium, utm_campaign, utm_content, utm_term,
//   referrer, landing_page, captured_at
// }
```

**Inferência automática (sem UTMs na URL):**

| Situação | utm_source | utm_medium |
|---|---|---|
| Veio do Google | `google` | `organic` |
| Veio do Instagram/Facebook | `meta` | `social` |
| Veio do LinkedIn | `linkedin` | `social` |
| Veio do YouTube | `youtube` | `social` |
| Outro referrer | hostname | `referral` |
| Sem referrer | `direct` | `none` |

**Persistência:**
- `sessionStorage` → last-touch (reseta ao fechar aba)
- `localStorage` → first-touch (nunca sobrescrito)
- Cookie `cadencia_utm` → lido server-side no callback OAuth (`SameSite=None;Secure`)

---

### 2. `src/components/UtmCapture.tsx`

Componente silencioso inserido no `layout.tsx`. Não renderiza nada.

- **Mount**: captura sempre (para orgânico/direct)
- **Route change**: re-captura só se a nova URL contém `utm_source` ou `utm_campaign`

Já está no layout — nenhuma ação necessária para novas páginas.

---

### 3. `src/lib/meta-pixel.ts`

Wrapper para `fbq` (browser) + chamada ao CAPI em paralelo.

```typescript
import {
  pixelPageView,           // só browser — em troca de rota
  pixelLead,               // browser + CAPI — após cadastro
  pixelCompleteRegistration, // browser + CAPI — após onboarding
  pixelInitiateCheckout,   // só browser — ao selecionar plano
  pixelPurchase,           // browser + CAPI — após pagamento confirmado
  pixelViewContent,        // só browser — visita a página importante
} from "@/lib/meta-pixel";

// Uso:
pixelLead(email);                          // no signup
pixelCompleteRegistration();               // no fim do onboarding
pixelPurchase(249.90, "pro");             // no webhook de pagamento
```

**Pixel ID:** `159019099458057` (Meta Events Manager → "Cadencia SaaS")

**Eventos que disparam CAPI:**

| Evento | Browser | CAPI | PII enviada |
|---|---|---|---|
| `PageView` | sim | não | — |
| `ViewContent` | sim | não | — |
| `Lead` | sim | sim | email SHA256 |
| `CompleteRegistration` | sim | sim | email SHA256 |
| `InitiateCheckout` | sim | não | — |
| `Purchase` | sim | sim | email SHA256 + valor |

---

### 4. `src/components/MetaPixelInit.tsx`

Injeta o script `fbq` no `<head>` via `next/script strategy="afterInteractive"`.
Registra `PageView` em cada troca de rota via `usePathname` + `useSearchParams`.

Já está no `layout.tsx` — nenhuma ação necessária.

**Ativa apenas se** `NEXT_PUBLIC_META_PIXEL_ID` estiver definido.

---

### 5. `src/app/api/capi/route.ts`

Endpoint server-side para envio de eventos ao Meta sem depender do browser.

```
POST /api/capi
Content-Type: application/json

{
  "event_name": "Lead",            // obrigatório
  "email": "user@email.com",       // opcional — hashed SHA256 server-side
  "phone": "5511999999999",        // opcional — hashed SHA256 server-side
  "value": 249.90,                 // opcional
  "currency": "BRL",               // opcional
  "content_name": "pro",           // opcional
  "order_id": "uuid",              // opcional — usado para deduplicação
  "event_source_url": "https://..."// opcional — URL da página
}
```

**Resposta:**
```json
{ "ok": true, "events_received": 1 }
{ "ok": false, "reason": "..." }   // nunca retorna 5xx — sempre 200
```

**Env vars necessárias (Vercel):**
- `META_PIXEL_ID` — ID do pixel (server-side)
- `META_CAPI_TOKEN` — token de acesso à Graph API

**Rota pública** — não requer autenticação (já em `PUBLIC_ROUTES` no middleware).

---

### 6. Attribution no Supabase

Salvo em `tenant_config.config.attribution` no momento do provisioning.

```sql
SELECT config->'attribution' FROM tenant_config WHERE tenant_id = '...';
```

```json
{
  "attribution": {
    "first_touch": {
      "utm_source": "facebook",
      "utm_medium": "paid_social",
      "utm_campaign": "cadencia-aquisicao-a",
      "utm_content": "img-autoridade-01",
      "utm_term": "perfil-a-medicos",
      "landing_page": "/?utm_source=facebook&utm_campaign=...",
      "captured_at": "2026-05-01T14:32:00.000Z"
    },
    "last_touch": {
      "utm_source": "direct",
      "utm_medium": "none",
      "landing_page": "/auth/sign-up",
      "captured_at": "2026-05-01T14:45:00.000Z"
    }
  }
}
```

**Fluxo por tipo de cadastro:**

| Cadastro | Como chega | Fallback |
|---|---|---|
| Email/senha | Body do `POST /api/auth/provision-tenant` | Cookie |
| Google OAuth | Cookie `cadencia_utm` lido no callback | — |

---

## Variáveis de Ambiente

| Variável | Onde | Valor |
|---|---|---|
| `NEXT_PUBLIC_META_PIXEL_ID` | Vercel (public) | `159019099458057` |
| `META_PIXEL_ID` | Vercel (server) | `159019099458057` |
| `META_CAPI_TOKEN` | Vercel (server) | token Meta API |

---

## Adicionar Novo Evento de Conversão

1. Adicionar função em `src/lib/meta-pixel.ts`:
```typescript
export function pixelMeuEvento(email?: string) {
  if (!PIXEL_ID) return;
  fbq("track", "MeuEvento", { content_name: "..." });
  sendCapi({ event_name: "MeuEvento", email });
}
```

2. Importar e chamar em `src/lib/analytics.ts`:
```typescript
import { pixelMeuEvento } from "./meta-pixel";

export function trackMeuEvento(email: string) {
  track("meu_evento", {});
  pixelMeuEvento(email);
}
```

3. Chamar `trackMeuEvento()` no ponto certo da UI.

---

## Testar em Produção

```bash
# CAPI direto
curl -X POST https://cadencia.app.br/api/capi \
  -H "Content-Type: application/json" \
  -d '{"event_name":"Lead","email":"test@gmail.com","content_name":"test"}'
# esperado: {"ok":true,"events_received":1}

# Verificar eventos no Meta Events Manager:
# business.facebook.com → Events Manager → Cadencia SaaS → Test Events
# Usar test_event_code "TEST_CADENCIA_DRY" no payload para modo de teste
```

---

## Verificar Attribution de um Tenant

```sql
-- Supabase SQL Editor
SELECT
  t.name,
  t.created_at,
  tc.config->'attribution'->'first_touch'->>'utm_source' AS source,
  tc.config->'attribution'->'first_touch'->>'utm_campaign' AS campaign,
  tc.config->'attribution'->'first_touch'->>'utm_content' AS ad_id,
  tc.config->'attribution'->'first_touch'->>'landing_page' AS landing
FROM tenants t
JOIN tenant_config tc ON tc.tenant_id = t.id
WHERE tc.config->'attribution' IS NOT NULL
ORDER BY t.created_at DESC
LIMIT 20;
```
