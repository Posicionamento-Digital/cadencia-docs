---
date: 2026-05-25
tags: [documentacao, cadencia, sub-squad, framework]
moc: "[[Cadencia-Framework/Docs/README]]"
projeto: Cadência
sub_squad: workers
type: source
entities: ["[[Cadencia]]"]
---
> 📍 Origem: `times/produto/cadencia/workers/CLAUDE.md` no `pd-framework`. Última sync: 2026-05-25.

# Sub-squad workers — Cadência

> Sub-squad aninhado dentro do Squad pai Cadência. Criado em sessão guiada com Felipe (2026-05-25 — PDL-239).

---

## Escopo

Backend Python da Cadência. Orchestrator 7-step + agents IA + renderer Playwright + integrations externas. Deploy Railway `master` hoje, migrando para Coolify VPS Master.

**Repo:** `felipeluissalgueiro/cadencia-app` (parte `cadencia-workers/`).
**Deploy hoje:** Railway via `git push origin main:master` (Dockerfile + healthcheck `/health` + restart on_failure 3 retries).
**Migração ativa:** Railway → Coolify VPS Master (cadeia PDL-18 a 23).

---

## Pipeline 7-step orchestrator

`src/workers/orchestrator.py`:

| Step | Agent | Função |
|---|---|---|
| 1 | Research Agent | Pesquisa tema (Método X/Y) |
| 2 | Model Selector | Classifica em 12 flags → seleciona modelo YAML (29 disponíveis) |
| 3 | Headline Agent | Headline + subtitle + hook_type |
| 4 | Carousel Agent | Slides JSON com componentes visuais |
| 5 | Caption Agent | Legenda Instagram + hashtags |
| 6 | Cover Generation | Gemini 2.5 Flash Identity Lock ou thematic |
| 7 | Slide Renderer | Playwright HTML→PNG 1080×1440 → Supabase Storage |

**Princípio (foundation/tech-principles.md #7):** pipeline é contrato. Features novas se encaixam como steps adicionais — não substituem.

---

## Agents (`src/workers/`)

- `caption_agent/`, `carousel_agent/`, `chat_agent/`, `headline_agent/`, `research_agent/`
- `dossier.py` — Big5 + DPR + Kane + Archetypes do tenant
- `editorials.py` — 3 categorias de post por tenant
- `ideas.py` — geração de ideias
- `instagram_publisher.py` — pub IG via OAuth
- `logo_analysis_agent.py` — análise logo upload
- `theme_agent.py`
- `visual_identity.py` — VI generation por tenant
- `rag.py` — retrieval
- `agent_memory.py` — memória dos agents
- `token_refresh.py` — refresh OAuth tokens
- `cover_generation.py` — Gemini Identity Lock
- `slide_renderer/` — Playwright HTML→PNG

---

## Templates e modelos

- **29 modelos YAML** (`src/models/*.yaml`): analise_profunda, animacao_processo, antes_depois, bastidores, citacao, comparacao, depoimento, desafio, dicas_rapidas, enquete_qa, entrevista, estudo_caso, expectativa_realidade, feedback_respostas, flash_sale, infografico, lista, meme_humor, motivacional, noticias, react_opinion, recapitulacao, resenha, storytelling, teste_quiz, transformacao, trend, tutorial, unboxing
- **7 famílias HTML** (`src/templates/family_*.html`): action, editorial, engagement, narrative, proof, statement, structured
- **Theme engine** (`src/shared/theme_engine.py` + `theme_css.py`) — base do renderer
- **Templates legados** (`src/templates/Templates_legados/`) — arquivo histórico

---

## Integrations externas

`src/integrations/`:
- `asaas/` — **legacy** (migrado Stripe 11/05 — dívida técnica rip)
- `ghl/` + `ghl.py` — GHL CRM/email/WhatsApp/Social Planner
- `llm/` — wrapper LLM (OpenAI/OpenRouter)
- `pexels.py` — stock images
- `supabase.py` — client server-side

---

## API FastAPI (`src/api/`)

- `routes/` — endpoints expostos
- `middleware/` — auth, RLS context, logging, errors

Healthcheck: `/health` (validado por Railway/Coolify).

---

## Tests (`tests/`)

- `test_orchestrator.py`
- `test_slide_renderer.py`
- `test_model_selector.py`
- `test_cover_generation.py`
- `test_llm_client.py`
- `test_model_config.py`
- `test_carousel_agent.py`
- `test_nuclear_coverage.py`
- `test_health.py`
- `visual/test_slide_contrast.py` — 40/40 PASS obrigatório se mexeu renderer

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| API | FastAPI |
| Renderer | Playwright (headless Chromium) |
| DB | Supabase Cloud (mesmo do produto) |
| Storage | Supabase Storage (slides + photos) |
| LLM texto | OpenAI (via OpenRouter — PR #2 em review) |
| LLM imagem | Gemini 2.5 Flash (Identity Lock) |
| Análise IG | Apify |
| Stock | Pexels |
| Deploy | Dockerfile + Procfile + railway.toml (hoje) → docker-compose Coolify (migração) |

---

## Workflows operacionais

- **Deploy hoje:** `git push origin main:master` → Railway build + healthcheck `/health` Ready
- **Migração ativa:** Coolify VPS Master (cadeia PDL-18 a 23)
- **Validação obrigatória:**
  - `npm run build` no monorepo zero erros
  - `python tests/visual/test_slide_contrast.py` 40/40 PASS (se mexeu renderer)
  - Rendi 1 post real local OU declarei NÃO testei
  - Pós-push: `railway logs` sem erro, healthcheck Ready
- **Princípio (foundation/tech-principles.md #8):** Compilou ≠ testou.

---

## Pessoas

- **Felipe** — dev principal + arquiteto pipeline
- **Time Dev cross-Time:** Vitor (arch), Amélia (dev), Camila (QA — tests)
- **Diego Infra** — apoio migração Coolify

---

## Bloqueios externos

| Bloqueio | Issue |
|---|---|
| **P1 — generation_queue schema (channel/channels)** | PDL-171 |
| Migração Railway → Coolify cadeia | PDL-18 a 23 |
| Liberar acesso Luiz Railway+Vercel | PDL-18 |
| Levantar workers e crons Railway pré-migração | PDL-19 |
| Migrar workers Railway → Docker Compose VPS | PDL-20 |
| Validar race condition pós-migração + cancelar Railway | PDL-21 |
| **Dívida Asaas** — código `integrations/asaas/` ainda existe | — |
| PR #2 OpenRouter via `OPENAI_BASE_URL/OPENAI_MODEL` | PR aberto |

---

## Histórico de incidents (do hub centralizado)

- **2026-04-26** — Vercel 7 deploys falharam silenciosos (TypeScript strict mode local ≠ prod)
- **2026-04-26** — Vercel env var com `\n` trailing newline → TRIGGER_SECRET mismatch persistente
- **2026-04-25** — Race condition Railway pega `generation_queue` antes do VPS (blog nunca gerava)
- **2026-04-15** — Apify post scraper campo errado — análise IG falhava silenciosamente
- **2026-05-19** — Migration RLS rejeitada por referência tabela inexistente `tenant_users`
- **2026-05-04** — `corpo_claro` texto invisível — NUCLEAR rule omissão recorrente (5+ fixes)

---

## Foundation — consulta obrigatória

Antes de criar:
- Step novo no orchestrator → `../foundation/tech-principles.md` #7 (pipeline é contrato)
- Mudança LLM provider → `../foundation/tech-principles.md` #6 (ADR formal exigido)
- Feature multi-tenant → `../foundation/multi-tenant-strategy.md`
- Mudança no renderer → `../foundation/tech-principles.md` #5 (Playwright HTML→PNG)

---

## Convenções

- **Branches:** `feat/pdl-XX-<desc>` (Felipe) ou `luiz/pdl-XX-<desc>` (Luiz)
- **Commits:** convencional (`feat(workers):`, `fix(workers):`, `chore(workers):`)
- **Deploy:** sempre `git push origin main:master` após push `main`
- **Tests visuais:** rodar antes de push se mexeu renderer ou template

---

## Refs

- `memory/STATE.md` — estado atual
- `memory/decisions.md` — decisões específicas
- `../CLAUDE.md` — manual Squad pai
- `../SOUL.md` § Princípios técnicos
- `../foundation/tech-architecture.md` § Workers backend
- Repo: `felipeluissalgueiro/cadencia-app/cadencia-workers/`
- Logs Railway: `railway logs`
- Healthcheck: `/health`
