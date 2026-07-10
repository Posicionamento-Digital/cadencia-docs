---
date: 2026-05-25
tags: [documentacao, cadencia, feature, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
type: source
entities: ["[[Cadencia]]"]
---
> 📍 Origem: `times/produto/cadencia/features/blog/README.md` no `pd-framework`. Última sync: 2026-05-25.

# Feature: Blog (white-label por tenant)

> Feature do Squad pai Cadência. **NÃO é sub-squad** (rebaixado durante bootstrap PDL-232 — decisão D03 em `../../memory/decisions.md`).

---

## O que é

Template **multi-tenant** de blog Next.js + Supabase. Cada tenant da Cadência tem uma instância própria deste template deployada no Vercel automaticamente. Conteúdo gerado pelo orchestrator (sub-squad `workers/`) → publicado via webhook → blog do tenant rebuilda.

---

## Por que NÃO é sub-squad

Critério HIERARCHY exige (pra ser Squad): CLAUDE.md próprio + memory próprio + workers cron próprios + ritmo independente.

Blog não tem nada disso:
- **Geração de conteúdo** vive em `workers/` (orchestrator 7-step + agents)
- **Auto-deploy** acontece em Vercel quando post aprovado (não tem cron próprio)
- **Template** raramente muda (mudança visual / fix CSS) — sem cadência de release
- **Sem equipe distinta** — mesma stack Next.js do frontend

Por isso → feature.

---

## Repos / artefatos

- **Template fonte:** `felipeluissalgueiro/cadencia-blog-template`
  - Stack: Next.js + Supabase + Vercel
  - Multi-tenant: lê posts do Supabase filtrados por `tenant_id`
  - Auto-deploy: webhook ao aprovar post → Vercel rebuild

- **Instância tenant:** `<slug-tenant>.cadencia-blog.app` (default) ou domínio próprio (add-on)
  - Estática (SSG/ISR)
  - Lê do mesmo Supabase Cloud
  - Cada tenant tem sua paleta + tipografia + identidade visual (VI)

- **Pasta local dev:** `Projetos BMAD/Cadencia/cadencia-blog/` (instância gerada pra dev/teste)

---

## Fluxo de publicação

```
[Sub-squad workers] orchestrator gera post → Supabase
    ↓
[Sub-squad growth] webhook publish → marca post como `approved`
    ↓
[Vercel] hook rebuild instância blog do tenant
    ↓
[Blog tenant] post visível em <slug>.cadencia-blog.app
```

---

## Quem opera

- **Mudanças no template** (visual, layout) → Time Dev (Vitor arch / Amélia dev) com handoff pra Squad pai Cadência
- **Geração de conteúdo** → sub-squad `workers/` (orchestrator)
- **Distribuição/publicação** → sub-squad `growth/` (webhook + scoring)

---

## Bloqueios / pendências

- PDL-24 — Compressão WebP no `blog_generate.py` (PNG 3MB → ~300KB)
- PDL-69 — Preview Vercel não funciona para teste (login redireciona produção)

---

## Refs

- `../../foundation/multi-tenant-strategy.md` § Blog Vercel template
- `../../foundation/tech-architecture.md` § Frontend / Blog por tenant
- Sub-squad `workers/` — geração
- Sub-squad `growth/` — distribuição
- Repo `cadencia-blog-template`

---

## Histórico

- **2026-05-25:** PDL-240 criada como sub-squad blog → rebaixada para feature durante bootstrap PDL-232. Decisão D03. PDL-240 fechada com Closes ajustado (criar este README).
