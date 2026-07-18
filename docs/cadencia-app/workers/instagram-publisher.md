> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-workers/src/workers/instagram-publisher/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-workers/src/workers/instagram-publisher/CLAUDE.md)
> Sincronizar via `/documentar-software` ou `sync_to_framework.py`.

---

# instagram-publisher — publicação no Instagram

## TL;DR

Publica carrossel/reels no Instagram do tenant via API do Instagram (Graph API). Chamado após aprovação de conteúdo.

## Identidade

- **Tipo:** Worker Python
- **Stack:** Python + Instagram Graph API + Supabase Storage
- **Path:** `cadencia-workers/src/workers/instagram_publisher.py`
- **Status:** ativo
- **Deps:** `published_posts`, Supabase Storage (slides PNG), `tenant_config.config.instagram`

## Dependências externas

- `logo_analysis_agent.py` — analisa logo do tenant para ajustar posicionamento na capa
- Instagram Graph API — requer `instagram_access_token` e `instagram_user_id` em `tenant_config`
- Análise de perfil Instagram: Apify (via `POST /api/instagram/analyze`)

## Como funciona

1. Recebe `content_document_id` do post aprovado
2. Carrega slides PNG do Supabase Storage
3. Faz upload de cada slide via Instagram Container API
4. Publica o carrossel (POST de mídia múltipla)
5. Atualiza `published_posts.instagram_published = true`

## Don'ts

- Token Instagram expira — verificar `instagram_token_expires_at` antes de publicar
- Não publicar sem slides renderizados — checar `rendering_status = completed` no `content_documents`

---

## Quando usar

- Publicação automática de carrossel/reels finalizados no Instagram do tenant.
- Disparado após pipeline-orchestrator concluir render com sucesso.

## Quando NÃO usar

- ❌ Para post de blog/seinfeld/newsletter — esses não vão para Instagram.
- ❌ Para preview/draft — só publica conteúdo aprovado.
- ❌ Tenant sem Instagram conectado — falha silenciosa, sem retry agressivo.

## Por que funciona assim

- Publicação separada do render para permitir review humano (admin) entre render e publish.
- Usa API oficial do Instagram via Facebook Graph (não scraping).

## 🚫 Don'ts

- **Não** publicar sem confirmação do tenant (modo auto-publish é opcional).
- **Não** repetir publicação ao reiniciar worker — idempotência via flag `instagram_posted`.
- **Não** publicar com legenda > 2200 chars (limite IG) sem truncar.

## 🪦 Já tentamos

- Publicação imediata sem revisão → conteúdo com erro visual indo ao ar. Razão de manter review humano padrão.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Post sai sem cover | Slide_renderer falhou em cover_generation | Reexecutar pipeline com fallback temático |
| Erro 429 do Graph API | Rate limit por conta | Backoff exponencial; queue de publicação |
| Legenda cortada | Excedeu 2200 chars | Truncar com `…` mantendo hashtags no fim |
| Tenant desconectou IG | Token expirado | Refluxo OAuth — notificar tenant |

## 📚 Referências cruzadas

- [pipeline-orchestrator](../CLAUDE.md) — Produtor
- [tracking-analytics](../../../../src/lib/analytics/CLAUDE.md) — Eventos de publicação
