---
date: 2026-05-14
tags: [cadencia, prd, produto, saas, carrossel, ia, tecnologia, automacao]
moc: "[[MOC-Projetos]]"
type: source
entities: ["[[Cadencia]]", "[[marketing]]"]
---
# PRD — Executive Summary (Cadencia.app)

## Pricing Atualizado (2026-03-26)

| Plano | Preço | Posts |
|---|---|---|
| Starter | R$119,90/mês | 10 posts |
| Pro | R$249,90/mês | 30 posts |
| Business | R$499,90/mês | 60 posts |

- Posicionamento ACIMA da concorrência (Posttar R$99/10 posts)
- Busca por tendências incluso desde Starter
- Novos formatos em todos os planos: Quick post, Antes/depois, Sessão de Fotos com IA

---

## Executive Summary

O Cadencia é um SaaS de geração automatizada de conteúdo para redes sociais. O cliente — empreendedor de pequeno/médio negócio ou profissional liberal — responde perguntas com botões, nunca digita, e recebe posts profissionais prontos para publicar.

O sistema entende o negócio do cliente (posicionamento, público, tom de voz, identidade visual), gera conteúdo com narrativa estratégica personalizada, e entrega carrosséis, legendas e hashtags otimizados.

**MVP:** Carrosséis Instagram em 9 formatos (lista, tutorial, news brief, storytelling, comparação, expectativa vs realidade, antes/depois, recapitulação, estudo de caso).

**Visão:** Multi-canal — newsletter, vídeos, distribuição massiva.

**Origem:** Sistema validado em produção (Marketing PD) com 31 skills, scripts Python e Playwright.

**Público:** Empreendedores PMEs + profissionais liberais (corretores, nutricionistas, coaches, consultores, fotógrafos, terapeutas).

**Stack:** Next.js (Vercel) + Python (Hetzner) + Supabase + Cloudflare + Asaas

---

## O Que Torna Especial

1. **Não é gerador de templates** — Dossiê de Marca + 3 editorias personalizadas + Método X/Y
2. **Pipeline de 4 agentes** — Pesquisa → Headline → Carrossel → Legenda (cada um consome só dados relevantes)
3. **9 modelos de carrossel** com seleção por regras determinísticas
4. **Renderização parametrizada** — 1 motor Playwright, N identidades visuais
5. **Ficha técnica** — custo real por carrossel rastreado. Margem mínima 100%
6. **UX para leigos** — Botões, swipe, 1 toque por ação. Zero digitação

---

## Classificação

| Atributo | Valor |
|---|---|
| Tipo | SaaS B2B/B2C (PWA multi-tenant) |
| Domínio | Marketing Automation / Content Generation |
| Complexidade | Média-alta |
| Contexto | Brownfield (sistema predecessor validado) |
| Frontend | Next.js na Vercel |
| Prioridade | Lançar MVP rápido. Demanda real, concorrentes surgindo. |

---

## Notas Relacionadas

- [[Projetos/Cadencia/Docs/PRD-Arquitetura-Tecnica]]
- [[Projetos/Cadencia/Docs/Epics-Stories-Visao-Geral]]
- [[Projetos/Cadencia/Docs/Motor-Grafico-Carrosseis-Doc-Tecnica]]
- [[Projetos/Cadencia/Docs/Roadmap-Produto-2026]]
- [[Projetos/Cadencia/Docs/Avatar-de-Marca]]
