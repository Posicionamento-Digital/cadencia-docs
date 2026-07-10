---
date: 2026-05-14
tags: [cadencia, prd, epics, stories, roadmap, produto]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]"]
---
# Epics & Stories — Visão Geral (Cadencia.app)

**Atualizado:** 2026-03-26
- Total stories: 59 (era 52)
- Epic 1: COMPLETO (8/8 done)
- Epic 2: 11 stories (+4 motor psicológico)
- Epic 3: 16 stories (+3 formatos simples e style resolver)

---

## 7 Epics, 59 Stories

| Epic | Stories | Entrega |
|---|---|---|
| 1. Fundação | 8 | Scaffold, design system, DB+RLS, auth, backend, proxy, landing |
| 2. Onboarding | 11 | 3 fases, 3 agentes (dossiê, visual, editorial), visualização |
| 3. Pipeline | 16 | Ideias, swipe, orchestrator, 4 agentes, renderer 9 modelos, fotos, realtime |
| 4. Consumo | 8 | Home, preview, copiar, salvar, regenerar, feedback, histórico |
| 5. Billing | 8 | Paywall, Asaas, webhooks, créditos, avulsos, graça, ficha técnica, E2E |
| 6. Scheduling | 3 | UI agenda, geração automática, notificações |
| 7. Admin | 5 | Dashboard, suspender, model router, flags, métricas |

---

## Ordem de Implementação

| Fase | Epics | Entrega |
|---|---|---|
| MVP funcional | 1 → 2 → 3 → 4 | Cliente gera e consome carrosséis (36 stories) |
| MVP lançável | + 5 | Monetização funciona (44 stories) |
| MVP completo | + 6 → 7 | Automação + controle admin (52 stories) |

---

## Validação

- 61/61 FRs cobertos
- 39 NFRs endereçados
- Zero forward dependencies
- Cada story completável por 1 dev
- ACs em Given/When/Then

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/PRD-Executive-Summary]]
- [[Projetos/Cadencia/Docs/PRD-Arquitetura-Tecnica]]
- [[Projetos/Cadencia/Docs/Motor-Grafico-Carrosseis-Doc-Tecnica]]
- [[Projetos/Cadencia/Docs/Roadmap-Produto-2026]]
