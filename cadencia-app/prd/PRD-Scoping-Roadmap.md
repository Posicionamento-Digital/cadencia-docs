---
date: 2026-05-14
tags: [cadencia, prd, roadmap, mvp, escopo, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[qualidade]]"]
---
# PRD — Scoping & Roadmap (Cadencia.app)

## MVP Strategy

**Abordagem:** Experience MVP — o mínimo que faz o cliente dizer "isso é profissional demais"

**Validação:** 50 tenants pagam após 3 grátis em 3 meses = PMF confirmado

**Equipe:** Felipe (produto) + Michel CTO (arquitetura) + 1 dev full-stack + Claude Code

---

## MVP (Phase 1) — 19 Capabilities

1. Auth magic link + tenant provisioning
2. Onboarding 3 fases
3. Dossiê + ID Visual + Editorias
4. Pipeline 4 agentes
5. 9 modelos carrossel + regras de seleção
6. Renderização Playwright por tenant
7. Card conteúdo (preview/copiar/salvar)
8. Swipe ideias
9. Feedback loop (checkbox + like/dislike + performance)
10. Créditos (3 grátis + planos)
11. Checkout Asaas hosted
12. GHL CRM + tags
13. Scheduler simples
14. Layout responsivo (mobile + desktop)
15. Feature flags (PostHog)
16. Admin endpoints
17. Model Router
18. Analytics (PostHog + Mixpanel)
19. Logo + ID Visual Cadencia

---

## Phase 2 — Growth (V1.1)

Multi-canal (Reels, LinkedIn, blog), newsletter, dark mode, multi-client agência, escolha de estilo, Meta API, fotos IA experimental, WhatsApp, on-demand, admin dashboard, form pagamento embutido, OAuth Instagram.

## Phase 3 — Expansion (V2+)

Distribuição massiva, Reels gerados, performance insights, plano agência N tenants, role viewer, gamificação, micro-blog SEO/AEO, self-hosting modelos.

---

## Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Qualidade em nichos desconhecidos | Benchmark automatizado, beta 10 nichos |
| Playwright lento | Pool workers, queue, timeout 30s |
| Provider IA indisponível | Fallback chain Model Router |
| Custo de tokens alto | Ficha técnica, alerta >$0.25 |
| Concorrente equivalente | Velocidade + profundidade editorial |
| Trial não converte | A/B test 1/3/5 grátis |
| Churn alto | Feedback detecta cedo |

---

## Landscape Competitivo

**Google Pomelli:** "limitado", "um lixo", "prometeu tudo e entregou nada" (feedback real de grupo com 200 membros, 2026-03-25)

**Cadencia vs. mercado:** Única ferramenta com Dossiê + Editorias + Método X/Y + Research Document. Concorrentes focam em templates visuais.

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/PRD-Executive-Summary]]
- [[Projetos/Cadencia/Docs/Epics-Stories-Visao-Geral]]
- [[Projetos/Cadencia/Docs/Roadmap-Produto-2026]]
- [[Projetos/Cadencia/Docs/PRD-Functional-Requirements]]
