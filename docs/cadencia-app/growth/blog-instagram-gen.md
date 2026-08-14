> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`Posicionamento-Digital/cadencia-growth` / `main` / `docs/blog-instagram-gen.md`](https://github.com/Posicionamento-Digital/cadencia-growth/blob/main/docs/blog-instagram-gen.md)
> Sincronizar via `/documentar-software` ou `sync_to_framework.py`.

---

# blog-instagram-gen — geração de blog e Instagram (VPS)

## TL;DR

2 scripts de geração que rodam na VPS: `blog_generate.py` gera o post e grava a publicação diretamente no Supabase. `instagram_generate.py` gera legenda/hashtags para Instagram (a publicação em si é feita pelos workers Coolify VPS Master).

## Identidade

- **Tipo:** Python scripts
- **Paths (VPS `/cadencia/`):**
  - `pipeline/blog_generate.py`
  - `pipeline/instagram_generate.py`
- **Status:** ativo
- **Deps:** `generation_queue`, `content_ideas`, `published_posts`, `tenant_config`

## blog_generate.py

1. Reivindica atomicamente uma row de `generation_queue` ou processa a ideia informada no modo direto.
2. Verifica deduplicação por `content_idea_id`; o índice único em `published_posts` é a garantia final contra corrida residual.
3. Gera o conteúdo long-form, HTML, metadados e imagem destacada.
4. Insere diretamente em `published_posts` com `html_content`, `status='published'`, `tenant_id` e URL final.
5. Marca `content_ideas.status='used'` e fecha a row da fila como `completed`.
6. O `cadencia-blog` lê a nova row na próxima requisição (`force-dynamic`, `revalidate = 0`, `cache: 'no-store'`). O worker atual não chama `POST /api/publish` e não dispara deploy/rebuild.

## instagram_generate.py

- Gera caption + hashtags para Instagram
- NÃO publica — publicação via `instagram_publisher.py` nos workers Coolify VPS Master
- Salva em `published_posts.instagram_caption`

## Don'ts

- Falha ao inserir `published_posts` marca o job como `failed` e interrompe esta geração.
- `instagram_generate.py` na VPS e `instagram_publisher.py` nos workers são coisas diferentes

---

## Quando usar

- Cron diário 11h BRT — blog gera primeiro, instagram depois (usa blog como insumo).
- Trigger on-demand para canais `blog` e `instagram`.

## Quando NÃO usar

- ❌ Para carrossel/reels (workers Coolify VPS Master).
- ❌ Usar este script como endpoint HTTP de publicação; ele é worker de geração.
- ❌ Bypassar o claim atômico ou remover o índice único de deduplicação.

## Por que funciona assim

- Blog primeiro (insumo) → Instagram + LinkedIn derivam dele.
- Escrita única no Supabase → o blog Next.js white-label renderiza dinamicamente sem webhook de invalidação.
- Claim CAS + índice único `(tenant_id, content_idea_id)` protegem contra cron e trigger processarem a mesma ideia.

## 🚫 Don'ts

- **Não** remover as guardas CAS/unique que tornam execuções concorrentes idempotentes.
- **Não** ignorar coluna `research_documents` correta no schema.
- **Não** publicar Instagram sem blog do dia.
- **Não** reintroduzir chamada a `/api/publish` apenas para revalidar cache: o runtime atual usa `no-store`.

## 🪦 Já tentamos

- **2026-04-25 — Blog batch concorrente posts duplicados**: ver `2026-04-25_blog-batch-concorrente-posts-duplicados.md`.
- **2026-04-25 — Blog generate coluna research errada**: ver `2026-04-25_blog-generate-coluna-research-errada.md`.
- **2026-04-21 — Disparo blog hang sem timeout subprocess**: ver incident.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Post duplicado | Regressão no claim CAS ou no índice único por ideia | Verificar `claim_queue_item()` e índice `(tenant_id, content_idea_id)` |
| Coluna research errada | Schema mudou, código antigo | Reconciliar `research_documents` column name |
| Blog trava 100% CPU | Subprocess sem timeout | Adicionar `timeout=` |
| Post foi gravado mas não aparece | `tenant_id`, `status`, `html_content` ou env do blog divergente | Conferir a row e o `TENANT_ID` da instância; não há ISR para forçar |

## 📚 Referências cruzadas

- [linkedin-generation](linkedin-generation.md) — Consumidor
- [seinfeld-email](seinfeld-email.md) — Derivado do blog
- [blog-tenant](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-blog/CLAUDE.md) — Destino de publicação
