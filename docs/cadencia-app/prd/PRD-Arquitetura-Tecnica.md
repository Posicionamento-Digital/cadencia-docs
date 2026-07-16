---
date: 2026-05-14
tags: [cadencia, prd, arquitetura, tecnico, stack, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---


# PRD — Arquitetura Técnica (Cadencia.app)

> **ARQUIVO HISTÓRICO / LEGADO.** Preservado para memória, auditoria e contexto de decisões. Não usar como documentação operacional atual.


## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js PWA, Vercel. SSR landing, CSR app. Push via service worker. |
| Backend | FastAPI Python, Hetzner VPS. Workers assíncronos. Docker. |
| DB | Supabase PostgreSQL + RLS. jsonb para Research Document, cost_breakdown, tenant_config. |
| Auth | Magic link (Supabase Auth). Sem senha. |
| Real-time | Supabase Realtime (log agentes trabalhando). |
| Storage | Supabase Storage (PNGs, logos). CDN Cloudflare. |
| Analytics | PostHog self-hosted (heatmap, replay, flags) + Mixpanel (behavior) |
| Pagamento | Asaas (checkout hosted MVP) |
| CRM | GHL via subprocess + curl |

---

## Pipeline de Geração (4 Agentes)

```
Ideia Aprovada (swipe)
    |
[Agente de Pesquisa] → Research Document JSON
    |
[Agente de Headline] → Headline + Subtítulo + Gancho + Tipo Hook
    |
[Agente de Carrossel] → 7-10 slides (Método X/Y)
    |
[Agente de Legenda] → Caption (P/R/Cr/Cp/CTA) + Hashtags
    |
Conteúdo Pronto
```

---



## Model Router

- Config em Supabase (troca sem deploy)
- Provider abstraction (Anthropic, OpenAI, Google, open-source)
- Tiers: premium / standard / fast
- Fallback chain por task_type
- Token tracking por operação

---

## Renderização

- 1 script `generate_slides.py` parametrizado por tenant_config
- CSS Custom Properties injetadas por tenant
- 9 modelos de carrossel = sequências de componentes reutilizáveis
- Seleção por regras determinísticas (if/else em tabela Supabase)

---



## Billing

- 1 crédito = 1 post pronto
- 3 grátis no trial
- Ficha técnica por carrossel (custo real em jsonb)
- Waste factor ~1.3x para regenerações
- Margem contribuição mínima: 100%

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/PRD-Executive-Summary]]
- [[Projetos/Cadencia/Docs/Motor-Grafico-Carrosseis-Doc-Tecnica]]
- [[Projetos/Cadencia/Docs/Epics-Stories-Visao-Geral]]
