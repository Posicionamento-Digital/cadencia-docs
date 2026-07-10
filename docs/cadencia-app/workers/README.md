# workers/ — Backend Python (Railway → Coolify VPS)

7 workers Python que rodam no `cadencia-app/cadencia-workers/`. Stack: **FastAPI + Playwright + OpenAI + Supabase**.

> **Migração em andamento:** Railway → Coolify VPS (PDL-18 a 23). Paths refletem estado pré-migração.

## Componentes

| Worker | Doc | Função em 1 linha | Entry point |
|---|---|---|---|
| **Pipeline Orchestrator** | [pipeline-orchestrator.md](pipeline-orchestrator.md) | Orquestra 7 steps para gerar carrossel ou reels a partir de uma ideia aprovada | `POST /api/v1/pipeline/run` |
| **Theme Engine** | [theme-engine.md](theme-engine.md) | Resolve qual sub-preset visual aplicar ao renderizar slides (15 opções) | Inline no step 7 do orchestrator |
| **Onboarding Workers** | [onboarding-workers.md](onboarding-workers.md) | 3 workers em sequência: dossier → visual-identity → editorials | `/api/v1/onboarding/*` |
| **Chat Ideias** | [chat-ideias.md](chat-ideias.md) | Chat "Tenho uma ideia" — usuário conversa com a IA da própria marca | `POST /api/v1/chat` |
| **Ideas Generator** | [ideas-generator.md](ideas-generator.md) | Geração programada de ideias (não-conversacional, complementa o chat) | `POST /api/v1/ideas` |
| **Instagram Publisher** | [instagram-publisher.md](instagram-publisher.md) | Publica carrossel/reels no Instagram via Graph API | Após render OK |
| **RAG Memory** | [rag-memory.md](rag-memory.md) | Memória vetorial por tenant + refresh de tokens periódico | Consumido pelos outros workers |

## Fluxo típico — geração de carrossel

```
content_idea aprovada (frontend)
  └─► POST /api/app/trigger-generation (Vercel)
       └─► filtra carrossel → Railway workers
            └─► pipeline-orchestrator (7 steps):
                 1. research_agent
                 2. model_selector (29 YAML)
                 3. headline_agent
                 4. carousel_agent
                 5. caption_agent
                 6. cover_generation (Gemini Identity Lock)
                 7. slide_renderer ← theme-engine inline
            └─► instagram-publisher (publica)
```

## Fluxo típico — onboarding novo tenant

```
fase 1 (frontend) → perfil básico
  └─► fase 2:
       dossier.py ─► tenant_dossier
                  └─► provision_soul_md (gera SOUL.md do tenant)
       visual_identity.py ─► 3 opções sub-preset (15 disponíveis)
       editorials.py ─► 3 editoriais com pesos [0.40, 0.35, 0.25]
  └─► fase 3 → finaliza → /app/preparing polling 5 ideias
```

## Stack consolidada

| Dependência | Onde |
|---|---|
| **Supabase** | `generation_queue`, `content_documents`, `published_posts`, `tenant_*` |
| **OpenAI (via OpenRouter)** | LLM de texto (research, headline, carousel, caption) |
| **Gemini 2.5 Flash** | Cover generation (Identity Lock) |
| **Playwright** | Render HTML → PNG (slides) |
| **GHL workers** | `integrations/ghl.py` (token global, location central PD) |
| **OpenRouter** | Roteamento LLM por agente |

## Cuidados transversais (Don'ts)

- **`generation_queue.channel`** (singular antigo) vs **`channels`** (plural novo) — PDL-171 pendente.
- **GHL no workers usa token global** (G004), não por tenant. Não confundir com seinfeld/scoring (que usam `location_pit_token` por tenant).
- **Schema cache do PostgREST** — após CREATE TABLE via Management API: `NOTIFY pgrst, 'reload schema'`.
- **Cleanup-stuck** roda a cada 15min — jobs em `processing` mais velhos viram `failed`.

## Refs

- Voltar: [`../README.md`](../README.md)
- ADR relevante: [`../adr/0004-carrossel-railway-resto-vps.md`](../adr/0004-carrossel-railway-resto-vps.md)
- Outro pólo (texto/email): [`../growth/`](../growth/)
- Fluxo end-to-end: [`../architecture/architecture.md`](../architecture/architecture.md)
