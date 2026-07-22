# src/app/api — guia para agentes

API routes do Next.js (Vercel). 9 grupos de rotas.

## Mapa de rotas

| Grupo | Path | O que faz |
|---|---|---|
| `app/` | `/api/app/*` | Operações do app autenticado (conteúdo, ideias, posts, créditos, admin, tickets, geração) |
| `auth/` | `/api/auth/*` | Auth e provisioning de tenant (`provision-tenant` cria tenant+plano no signup) |
| `capi/` | `/api/capi/*` | Meta Conversions API (eventos de conversão) |
| `instagram/` | `/api/instagram/*` | Análise de perfil Instagram (Apify) |
| `onboarding/` | `/api/onboarding/*` | Fluxo de onboarding (fases 1, 2, 3) |
| `stevo/` | `/api/stevo/*` | WhatsApp via Stevo (notificações internas) |
| `v1/` | `/api/v1/*` | API interna — workers Python chamam daqui |
| `webhooks/` | `/api/webhooks/*` | Webhooks de pagamento Stripe |

## Rotas críticas

| Rota | Função |
|---|---|
| `POST /api/auth/provision-tenant` | Signup: cria tenants + users + roles + onboarding + plano trial (3 créditos) |
| `POST /api/app/trigger-generation` | On-demand: filtra carrossel/reels (workers Coolify VPS Master) e envia restante ao VPS porta 39090 |
| `GET /api/app/generation-queue` | Status da fila de geração |
| `POST /api/app/content/[id]/publish` | Publica conteúdo aprovado |
| `POST /api/webhooks/stripe` | Processa pagamentos e créditos com idempotência |

## Fluxo trigger-generation

```
Scheduler externo (disparador não confirmado — ver Foundation - Tech Architecture §Cron jobs)
  → POST /api/app/trigger-generation (Vercel)
  ├─ carrossel / reels → workers Coolify VPS Master
  └─ blog / seinfeld / linkedin / instagram → VPS porta 39090
```

## Como ler o código

```bash
gh api "repos/felipeluissalgueiro/cadencia-app/contents/src/app/api/<path>?ref=master" \
  | python -c "import json,sys,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

---

## Quando usar

- Toda rota servidor do Next.js mantém a fronteira entre frontend, workers, VPS, Supabase e Stripe.

## Quando NÃO usar

- ❌ Para lógica que precisa de >10s — usar workers Coolify VPS Master (timeout Vercel).
- ❌ Para acesso direto a DB de outro tenant — usar service_role com cuidado.
- ❌ Substituir webhooks externos — Stripe chama aqui, não o contrário.

## Por que funciona assim

- Vercel para latência baixa em rotas síncronas (auth, trigger).
- `trigger-generation` filtra canais e roteia (workers Coolify vs VPS growth) — single point of dispatch.
- v1 isolada para chamadas de workers — separa "público" (app) de "interno" (workers).

## 🚫 Don'ts

- **Não** chamar workers Coolify/VPS direto do client — sempre via `/api/app/*`.
- **Não** ignorar timeout Vercel (10s hobby, 60s pro) — operações pesadas vão pra worker.
- **Não** misturar service_role com endpoints públicos — RLS bypassa.
- **Não** assumir que `v1/*` é seguro — exige auth shared-secret.

## 🪦 Já tentamos

- **2026-04-26 — Trigger secret mismatch silenciosa**: env var Vercel com trailing newline. Pipeline rodava 0x. Ver incident.
- **2026-04-26 — Vercel env var trailing newline secret mismatch**: ver incident.
- **2026-04-15 — Vercel 6 deploys falharam**: ver `2026-04-15_vercel-6-deploys-falharam.md`.
- **2026-04-26 — Vercel 7 deploys falharam typescript strict**: ver incident.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| `trigger-generation` retorna 200 mas nada gera | Secret mismatch (env trailing newline) | Re-setar var no Vercel sem newline |
| Timeout em endpoint | >10s no Vercel | Migrar para worker async |
| 401 em `/api/v1/*` | Shared secret errado | Conferir `VPS_TRIGGER_SECRET` env nos dois lados |
| Webhook Stripe 400 | Signature mismatch | Conferir `STRIPE_WEBHOOK_SECRET` |
| Build falha TS strict | Var não usada / typing | Ver incidents Vercel |

## 📚 Referências cruzadas

- [api-auth-provisioning](auth/CLAUDE.md)
- [api-integrations](webhooks/CLAUDE.md)
- [payment-billing](app/billing/CLAUDE.md)
- [growth-pipeline-runner](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/growth-pipeline-runner.md) — Consumidor do trigger
