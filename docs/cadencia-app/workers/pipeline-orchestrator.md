> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `cadencia-workers/src/workers/CLAUDE.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/cadencia-workers/src/workers/CLAUDE.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# pipeline-orchestrator — agente de geração de carrossel/reels

## TL;DR

Recebe uma `content_idea` aprovada e executa 7 steps em sequência para produzir slides renderizados (PNG). Entry point: `POST /api/v1/pipeline/run`.

## Identidade

- **Tipo:** Worker backend Python
- **Stack:** FastAPI + OpenAI (OpenRouter) + Playwright
- **Path:** `cadencia-workers/src/workers/orchestrator.py` + `src/api/routes/pipeline.py`
- **Status:** ativo (Railway; migrando → Coolify VPS)
- **Deps:** Supabase (`generation_queue`, `content_documents`, `published_posts`), `research_agent`, `model_selector`, `headline_agent`, `carousel_agent`, `caption_agent`, `cover_generation`, `slide_renderer`

## Como funciona — 7 steps

| Step | Módulo | Output |
|---|---|---|
| 1 `research` | `research_agent.generate_research` | Contexto sobre o tema + editorial + dossier |
| 2 `model_selection` | `model_selector.select_carousel_model` | Qual dos 29 YAML models usar por editorial function |
| 3 `headline` | `headline_agent.generate_headline` | Headline + subtitle + hook_type |
| 4 `carousel` | `carousel_agent.generate_carousel` | Lista de slides com texto + imagens Pexels |
| 5 `caption` | `caption_agent.generate_caption` | Caption Instagram + hashtags |
| 6 `cover_generation` | `cover_generation.generate_cover` / `generate_thematic_cover` | Capa: pessoa (GPT-image-1 + foto rosto) ou temática ou skip |
| 7 `rendering` | `slide_renderer.render_slides` | HTML templates → PNG (Playwright) |

`theme_agent.generate_theme` é chamado inline no step 7 se `tenant_themes` não tiver registro para o tenant.

## Filas e status

- `generation_queue` table: `created → processing → completed | failed`
- `POST /api/v1/pipeline/run` verifica duplicata antes de enfileirar
- `multi_version=true` cria até 3 jobs em paralelo (versões A/B/C)
- `cleanup-stuck`: jobs em `processing` > 15min são marcados `failed`

## Deduplicação de imagens

`carousel_agent` usa prefixo de nicho + histórico cross-post para evitar repetir imagens Pexels entre posts do mesmo tenant.

## Quando NÃO usar

- NÃO chamar diretamente — sempre via `POST /api/v1/pipeline/run`
- NÃO usar para blog/seinfeld/linkedin/newsletter — esses vão para VPS trigger_server.py
- Carrossel e reels: este pipeline. Resto: VPS.

## Don'ts

- `generation_queue.channel` vs `channels` — cuidado com schema (PDL-171 pendente)
- Nunca alterar steps sem atualizar `step_names` no route de status

---

## Quando usar

- Geração de **carrossel** ou **reels** disparada por aprovação de ideia no frontend (`POST /api/app/trigger-generation`).
- Reexecução manual via admin (botão "Regerar" no `/app/admin`).
- Job de catch-up de carrossel após resolver bug crítico (rodar batch para tenants afetados).

## Quando NÃO usar

- ❌ Geração de **blog/seinfeld/linkedin/instagram/newsletter** — vai por `trigger_server.py` VPS, não por este orchestrator. Ver [ADR-0004](../../../../docs/adr/0004-carrossel-railway-resto-vps.md).
- ❌ Chamar diretamente bypassando `generation_queue` — quebra dedup + cleanup-stuck.
- ❌ Pipeline para tenant sem `tenant_dossier` e 3 editoriais — falha em step `research`.

## Por que funciona assim

- [ADR-0004](../../../../docs/adr/0004-carrossel-railway-resto-vps.md) — Carrossel/reels Railway, resto VPS.
- 7 steps explícitos (não 1 prompt gigante) — facilita observabilidade, retry, A/B de prompts por step.
- `multi_version` paralelo: gera A/B/C de uma vez para testar variações sem custo extra de research.

## 🚫 Don'ts

- **Não** alterar a ordem dos steps sem alinhar com `step_names` no route de status — quebra a UI de progresso.
- **Não** chamar workers diretos (`carousel_agent`, `cover_generation`) — sempre via orchestrator (dedupe + status).
- **Não** subir nova versão de `slide_renderer` em produção sem rodar batch de visual regression — bugs visuais já machucaram (38 bugs detectados em batch — ver incident `renderer-38-bugs-visuais`).
- **Não** confundir schema `generation_queue.channel` (singular antigo) com `channels` (plural novo) — PDL-171 pendente.

## 🪦 Já tentamos

- **2026-04-25 — Renderer 38 bugs visuais**: deploy de nova versão sem batch de visual regression. Ver `pd-framework/incidents/2026-04-25_renderer-38-bugs-visuais-batch1-batch2.md`.
- **2026-04-25 — Race condition Railway vs VPS** na `generation_queue`: dois consumers tentando processar mesmo job. Fix: lock pessimista + `processed_by` field. Ver `2026-04-25_race-condition-generation-queue-railway-vps.md`.
- **2026-05-15 — Ideias presas em "processing"** com spinner eterno: jobs travados sem cleanup-stuck rodando. Ver `2026-05-15_ideias-presas-processing-spinner-eterno.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Spinner eterno no `/app/ideas` | Job parado em `processing` > 15min sem cleanup | Forçar `cleanup-stuck` endpoint ou `UPDATE generation_queue SET status='failed' WHERE status='processing' AND created_at < NOW() - INTERVAL '15 minutes'` |
| Step `research` falha 100% | Tenant sem dossier/editoriais | Rodar onboarding-workers antes |
| Step `cover_generation` falha | Sem foto rosto + sem fallback temático configurado | Adicionar foto em `tenant_config.config.face_image_url` ou aceitar capa skip |
| Carrossel renderizado com texto cortado/sobreposto | Bug visual no template | Visual regression batch + abrir incident |
| Dois jobs iguais aparecem | Dedup falhou (race) | Confirmar lock + `processed_by`. Ver incident race-condition |

## 📚 Referências cruzadas

- [theme-engine](../theme-engine/CLAUDE.md) — Chamado inline no step 7
- [cadencia-workers/CLAUDE.md](../../../CLAUDE.md) — Overview workers
- [docs/architecture.md](../../../../docs/architecture.md) — Nível 2 Container
- [CONTEXT.md](../../../../CONTEXT.md) — Generation queue, content idea, published post
