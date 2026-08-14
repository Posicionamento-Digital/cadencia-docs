> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-blog/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-blog/CLAUDE.md)
> Sincronizar via `/documentar-software` ou `sync_to_framework.py`.

---

# blog-tenant — blog white-label por tenant

## TL;DR

Projeto Next.js standalone (`cadencia-blog/`) com deploy separado no Vercel por tenant. Cada tenant tem um blog próprio com domínio e identidade visual individuais. As páginas são renderizadas dinamicamente e consultam o Supabase a cada request.

## Identidade

- **Tipo:** Next.js 16 standalone (App Router)
- **Path:** `cadencia-blog/`
- **Deploy:** Vercel auto-deploy por tenant, ligado ao repo Git dedicado `blog-<tenant_slug>`
- **Status:** ativo
- **Deps:** Supabase REST (`published_posts`, `tenant_config`, `tenant_profile`)

## Estrutura

```
cadencia-blog/
  src/app/
    page.tsx              # home — lista de posts
    posts/[slug]/page.tsx # post individual
    api/publish/route.ts  # endpoint alternativo autenticado de upsert
    robots.txt/route.ts   # SEO
    sitemap.xml/route.ts  # SEO
```

## Fluxo de publicação

1. Growth pipeline (VPS) gera o post e grava diretamente em `published_posts`.
2. Home e página de post executam como `force-dynamic`, com `revalidate = 0` e fetch `cache: 'no-store'`.
3. A próxima requisição lê o post atualizado diretamente do Supabase; não há rebuild nem invalidação ISR.
4. `POST /api/publish` continua disponível como endpoint alternativo de upsert protegido por `PUBLISH_SECRET`, mas o worker atual `blog_generate.py` não o chama.

## Identidade visual por tenant

Resolvida no Supabase a partir do `TENANT_ID` configurado na instância:
- `tenant_config`: cores, fontes e configurações do blog
- `tenant_profile`: identidade e dados complementares
- Domínio customizado: configurado no projeto Vercel do tenant

## Don'ts

- Falha ao gravar `published_posts` aborta a geração; não confundir com cache ou rebuild do blog.
- Alterar o template não atualiza automaticamente repos de tenants já criados. A mudança precisa ser propagada e deployada nos repos dedicados afetados.

---

## Quando usar

- Renderização do blog white-label de um tenant.
- `POST /api/publish` somente para integrações que precisem fazer upsert pelo próprio blog e possuam `PUBLISH_SECRET`.

## Quando NÃO usar

- ❌ Como blog institucional da Cadencia — esse é `(marketing)/` no app principal.
- ❌ Tenant sem deploy Vercel configurado — falha silenciosa.
- ❌ Compartilhar uma instância entre vários tenants enquanto o código depender de um único `TENANT_ID`.
- ❌ Chamar `POST /api/publish` sem `PUBLISH_SECRET` configurado nos dois lados.

## Por que funciona assim

- 1 instância Vercel + 1 repo Git dedicado por tenant — isolamento de domínio, configuração e deploy; também evita o limite Hobby de projetos conectados ao mesmo repo.
- SSR dinâmico sem cache — elimina a necessidade de ISR/rebuild quando um post é publicado.
- Endpoint alternativo protegido por secret — mantém compatibilidade com integrações de publicação sem expor escrita anônima.

## 🚫 Don'ts

- **Não** expor ou commitar `PUBLISH_SECRET` e `SUPABASE_SERVICE_KEY`.
- **Não** adicionar uma dependência de `revalidateTag`/`revalidatePath` sem antes mudar as páginas de `no-store` para uma estratégia de cache explícita.
- **Não** apontar múltiplos tenants para a mesma instância enquanto a resolução continuar baseada em `TENANT_ID` de ambiente.
- **Não** assumir que commit no `cadencia-blog-template` atualiza repos `blog-*` já gerados.

## 🪦 Já tentamos

- **2026-04-25 — Blog batch concorrente posts duplicados**: ver `2026-04-25_blog-batch-concorrente-posts-duplicados.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Post novo não aparece | Row ausente/errada em `published_posts`, `tenant_id` divergente ou erro de leitura Supabase | Conferir row, env `TENANT_ID` e logs; não existe `/api/revalidate` no runtime atual |
| Build falha por tenant | Env vars incompletas no Vercel | Reconciliar com painel |
| Domínio aponta para 404 | DNS não propagou | Aguardar + conferir CNAME |
| 401 no `/api/publish` | Secret mismatch | Conferir env nos dois lados |
| Fix do template não chega ao tenant | Repo dedicado não recebeu a mudança | Propagar o commit ao repo do tenant e executar deployment controlado |

## 📚 Referências cruzadas

- [blog-instagram-gen](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/blog-instagram-gen.md) — Produtor
- [growth-pipeline-runner](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/growth-pipeline-runner.md)
