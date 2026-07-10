> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`Posicionamento-Digital/cadencia-growth` / `main` / `docs/blog-instagram-gen.md`](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/blog-instagram-gen.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# blog-instagram-gen — geração de blog e Instagram (VPS)

## TL;DR

2 scripts de geração que rodam na VPS: `blog_generate.py` gera post de blog e faz deploy via webhook. `instagram_generate.py` gera legenda/hashtags para Instagram (a publicação em si é feita pelos workers Railway).

## Identidade

- **Tipo:** Python scripts
- **Paths (VPS `/cadencia/`):**
  - `pipeline/blog_generate.py`
  - `pipeline/instagram_generate.py`
- **Status:** ativo
- **Deps:** `published_posts`, `tenant_config`, cadencia-blog webhook

## blog_generate.py

1. Gera post de blog via LLM (conteúdo long-form baseado no editorial do post)
2. Salva em `published_posts.blog_content` + `published_posts.published=true`
3. Chama `POST /api/publish` no blog tenant (cadencia-blog) para revalidar cache
4. Se blog falha → `trigger_server.py` aborta o restante da pipeline (G — blog é pré-requisito)

## instagram_generate.py

- Gera caption + hashtags para Instagram
- NÃO publica — publicação via `instagram_publisher.py` nos workers Railway
- Salva em `published_posts.instagram_caption`

## Don'ts

- Blog failure = abort da pipeline. Fix bugs aqui tem prioridade
- `instagram_generate.py` na VPS e `instagram_publisher.py` nos workers são coisas diferentes

---

## Quando usar

- Cron diário 11h BRT — blog gera primeiro, instagram depois (usa blog como insumo).
- Trigger on-demand para canais `blog` e `instagram`.

## Quando NÃO usar

- ❌ Para carrossel/reels (Railway).
- ❌ `trial`/`essencial`/`starter` fora de seg+qui (frequência restrita).
- ❌ Blog em batch concorrente — gera duplicação.

## Por que funciona assim

- Blog primeiro (insumo) → Instagram + LinkedIn derivam dele.
- Render HTML em template Jinja → publicação automática no `cadencia-blog` (Next.js estático, white-label por tenant).

## 🚫 Don'ts

- **Não** rodar 2 instâncias do `blog_generate.py` simultaneamente para o mesmo tenant — duplica post.
- **Não** ignorar coluna `research_documents` correta no schema.
- **Não** publicar Instagram sem blog do dia.

## 🪦 Já tentamos

- **2026-04-25 — Blog batch concorrente posts duplicados**: ver `2026-04-25_blog-batch-concorrente-posts-duplicados.md`.
- **2026-04-25 — Blog generate coluna research errada**: ver `2026-04-25_blog-generate-coluna-research-errada.md`.
- **2026-04-21 — Disparo blog hang sem timeout subprocess**: ver incident.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Post duplicado | Batch concorrente; sem lock | Lock pessimista por tenant antes de gerar |
| Coluna research errada | Schema mudou, código antigo | Reconciliar `research_documents` column name |
| Blog trava 100% CPU | Subprocess sem timeout | Adicionar `timeout=` |

## 📚 Referências cruzadas

- [linkedin-generation](linkedin-generation.md) — Consumidor
- [seinfeld-email](seinfeld-email.md) — Derivado do blog
- [blog-tenant](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-blog/CLAUDE.md) — Destino de publicação
