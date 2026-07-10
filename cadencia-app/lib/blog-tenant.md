> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-blog/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-blog/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# blog-tenant — blog white-label por tenant

## TL;DR

Projeto Next.js standalone (`cadencia-blog/`) com deploy separado no Vercel por tenant. Cada tenant tem um blog próprio com domínio e identidade visual individuais.

## Identidade

- **Tipo:** Next.js 15 standalone (App Router)
- **Path:** `cadencia-blog/`
- **Deploy:** Vercel auto-deploy por tenant (variáveis de ambiente por instância)
- **Status:** ativo
- **Deps:** Supabase (`published_posts`), webhook `POST /api/publish`

## Estrutura

```
cadencia-blog/
  src/app/
    page.tsx              # home — lista de posts
    posts/[slug]/page.tsx # post individual
    api/publish/route.ts  # webhook revalidate
    robots.txt/route.ts   # SEO
    sitemap.xml/route.ts  # SEO
```

## Fluxo de publicação

1. Growth pipeline (VPS) gera post e salva em `published_posts`
2. Chama `POST /api/publish` no blog do tenant
3. Next.js faz `revalidateTag` → invalidar cache do post
4. Post aparece no blog do tenant

## Identidade visual por tenant

Injetada via variáveis de ambiente Vercel por instância:
- Cores, fontes, logo
- Domínio customizado

## Don'ts

- Blog failure no `blog_generate.py` aborta a pipeline de conteúdo — deploy do blog é crítico
- Não editar `cadencia-blog/` esperando mudança automática — requer novo deploy Vercel por tenant

---

## Quando usar

- Publicação de blog post de um tenant — auto-deploy por instância Vercel.
- Webhook `POST /api/publish` chamado pelos workers VPS após gerar blog post.

## Quando NÃO usar

- ❌ Como blog institucional da Cadência — esse é `(marketing)/` no app principal.
- ❌ Tenant sem deploy Vercel configurado — falha silenciosa.
- ❌ Sem `BLOG_PUBLISH_SECRET` — qualquer um poderia publicar.

## Por que funciona assim

- 1 instância Vercel por tenant — isolamento de domínio, identidade visual, performance.
- Estático + ISR — SEO bom + revalidação ao publicar via webhook.
- Webhook secret-based — autenticação leve, suficiente para uso interno.

## 🚫 Don'ts

- **Não** expor `BLOG_PUBLISH_SECRET` ou commitar.
- **Não** publicar sem revalidate — conteúdo novo não aparece sem ISR trigger.
- **Não** misturar blog de tenants na mesma instância — quebra brancagem.

## 🪦 Já tentamos

- **2026-04-25 — Blog batch concorrente posts duplicados**: ver `2026-04-25_blog-batch-concorrente-posts-duplicados.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Post novo não aparece | ISR não revalidou | Forçar via `/api/revalidate` |
| Build falha por tenant | Env vars incompletas no Vercel | Reconciliar com painel |
| Domínio aponta para 404 | DNS não propagou | Aguardar + conferir CNAME |
| 401 no `/api/publish` | Secret mismatch | Conferir env nos dois lados |

## 📚 Referências cruzadas

- [blog-instagram-gen](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/blog-instagram-gen.md) — Produtor
- [growth-pipeline-runner](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/growth-pipeline-runner.md)
