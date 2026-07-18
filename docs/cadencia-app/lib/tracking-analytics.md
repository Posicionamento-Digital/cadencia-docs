> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `src/lib/analytics/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/src/lib/analytics/CLAUDE.md)
> Sincronizar via `/documentar-software` ou `sync_to_framework.py`.

---

# tracking-analytics — analytics e rastreamento

## TL;DR

Stack de analytics: Mixpanel (produto) + PostHog (feature flags + heatmaps) + GA4 (tráfego) + GTM (tag manager) + Meta Pixel + CAPI (conversões).

## Identidade

- **Tipo:** Analytics stack (client-side + server-side)
- **Paths:**
  - `src/lib/analytics.ts`, `mixpanel.ts`, `posthog.ts`, `meta-pixel.ts`
  - `src/app/api/capi/` — Meta CAPI server-side
  - `scripts/analytics_pipeline.py` — relatórios GA4 + PostHog + Mixpanel
- **Status:** ativo
- **Deps:** GA4 `530321533`, PostHog, Mixpanel, Meta Pixel, GTM

## Fontes de dados

| Ferramenta | Fonte | O que mede |
|---|---|---|
| Mixpanel | Client-side events | Funil de produto (ideias aprovadas, posts gerados, etc.) |
| PostHog | Client-side + feature flags | Feature adoption, session recording, flags |
| GA4 | GTM + pageviews | Tráfego, landing pages, conversões |
| Meta Pixel | Client-side | Conversões (complementado por CAPI) |
| Meta CAPI | Server-side (API route) | Conversões server-side (mais confiável) |

## analytics_pipeline.py (scripts/)

- Lê GA4 (`GA4_PROPERTY_ID=530321533`) + PostHog + Mixpanel
- Gera relatório em `docs/analytics-reports/YYYY-MM-DD.md`
- **NÃO está integrado ao sistema de produção** — script manual para Felipe

## Don'ts

- `analytics_notion.py` foi deletado (Notion descontinuado) — usar `analytics_pipeline.py` e salvar no Obsidian
- PostHog feature flags: não usar para flags críticas de billing/auth — usar `tenant_config` diretamente

---

## Quando usar

- Tracking client-side (Mixpanel, PostHog, Meta Pixel) — eventos de produto + funil.
- Tracking server-side (CAPI) — deduplicação client+server, mais confiável para Meta.
- Relatório agregado pelo `analytics_pipeline.py` (manual, Felipe roda).

## Quando NÃO usar

- ❌ Para auditoria/financeiro — usar logs estruturados em Supabase, não Mixpanel.
- ❌ Para flags críticas — PostHog para A/B leve; `tenant_config` para crítico.
- ❌ Notion descontinuado — `analytics_notion.py` foi removido; saída agora vai para Obsidian.

## Por que funciona assim

- Múltiplas ferramentas com função distinta (Mixpanel=funil, PostHog=flags+session, GA4=tráfego) — cada uma ótima para seu eixo.
- CAPI server-side aumenta confiabilidade de tracking de conversão (iOS 14+ etc).

## 🚫 Don'ts

- **Não** mandar PII para Meta Pixel sem hash SHA256.
- **Não** duplicar evento client + server sem `event_id` compartilhado.
- **Não** confiar só em Mixpanel para revenue — Stripe é fonte da verdade.
- **Não** habilitar session recording PostHog em rotas com PII sensível.

## 🪦 Já tentamos

- Tracking só client-side → conversão Meta caía drasticamente em iOS 14+. Razão do CAPI.
- Manter analytics em Notion → custo manutenção alto, migrou para Obsidian.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Mixpanel zerado para tenant | `MIXPANEL_TOKEN` env errado | Verificar Vercel env |
| CAPI evento não chegou | Token inválido / signature | Logar resposta + retry |
| GA4 tráfego inconsistente | GTM tag desconfigurada | Auditar container GTM |
| `analytics_pipeline.py` falha | API key GA4 / PostHog rotacionada | Atualizar via 1Password |

## 📚 Referências cruzadas

- [lib-integrations](../CLAUDE.md) — Mixpanel/PostHog/Meta wrappers
- [api-integrations](../../app/api/webhooks/CLAUDE.md) — `/api/capi`
- Skill `/analytics-report` — Relatório cruzado para Obsidian
