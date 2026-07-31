# RFC-002: Extração+retry resiliente de JSON do LLM (guard content vazio)

> **Status:** Rascunho
> **Data:** 2026-07-24
> **Autor:** Felipe (via /linear-rfc) — arquitetura: Vitor (Tech Lead)
> **Projeto Linear:** Cadência — Roadmap
> **Issue:** DEV-1522
> **Origem:** incidente `incidents/2026-07-24_carousel-grok-content-vazio-parse-char0_5why.md` (pd-framework) + `/debug-5why`

## Contexto

O grok-4.20 (reasoning model, usado em `carousel`, `headline`, `caption`, `ideas`, `narrative`) devolve intermitentemente `choice.message.content == ""` (string vazia, não `None`) — gasta tokens no raciocínio e retorna content vazio. Hoje isso quebra a geração de post porque:

1. `llm.py::_generate_sync` guarda só `content is None` (linha 217) — string vazia passa e vira `text=""`.
2. Os workers fazem `json.loads(text)` → estoura `Expecting value: line 1 column 1 (char 0)`.
3. O `AgentResult.fail(retry=True)` é **morto** no path do pipeline (`orchestrator._fail_job` só marca failed e retorna; `retry_suggested` só é consumido em rotas de API como HTTP 503) — 1 sorteio ruim = falha terminal, sem retry.
4. Co-lateral: `_fail_job` não reseta `content_ideas.status`, deixando a ideia presa em `processing`.

A mesma dupla `json.loads` + `fail(retry=True)`-sem-retry se repete em `carousel_agent.py`, `dossier.py`, `editorials.py`, `ideas.py` — é uma **classe** de bug, não um ponto isolado (2º incidente no mesmo `llm.py`; irmão: 2026-07-03 httpx-remoteprotocol).

## Decisão central (grill)

**Opção C — 2 camadas ortogonais, entregues em 2 fatias.**

- **Camada transporte** (`_generate_sync`): trata `content` vazio/whitespace como falha **retriável** (mesmo tratamento hoje dado a `None`+transiente), retentando dentro do loop existente (`MAX_RETRIES`, backoff). Beneficia todo LLM call.
- **Camada semântica** (`generate_json`): helper novo que faz chamada → parse → validação de shape → retry, com contrato explícito. Os 5 workers que esperam JSON passam a usar.

Fatiamento:
- **Fatia 1 (fix imediato):** guard de content vazio em `_generate_sync` + reset de idea em `_fail_job`. Fecha o Fato Zero em produção.
- **Fatia 2 (sistêmico/DRY):** `generate_json` + migração dos 5 workers + telemetria + testes.

## Componentes

- **`_generate_sync` (llm.py)** — camada transporte. Responsável por: chamar o provider, aplicar retry em erros transientes **e agora em content vazio/whitespace**, devolver `LLMResponse` com `text` garantidamente não-vazio OU levantar após N tentativas.
- **`generate_json(prompt, task_type, *, retries, validate=None)` (llm.py, novo)** — camada semântica. Responsável por: invocar `_generate_sync`, strip de fences markdown, `json.loads`, validação opcional de shape (callback), retry próprio se parse/validação falha, e erro tipado após N.
- **Workers (`carousel_agent`, `dossier`, `editorials`, `ideas`, `narrative`)** — consumidores. Passam a chamar `generate_json` em vez de `_generate_sync`+`json.loads` inline.
- **`_fail_job` (orchestrator.py)** — reset de estado. Ao falhar, além de queue/status=failed, reseta `content_ideas.status 'processing'→'pending'`.

## Contratos entre componentes

- **`_generate_sync` → caller:** entrada `(prompt, max_tokens, tenant_id, task_type)`; saída `LLMResponse(text!="", input_tokens, output_tokens, model)`. Erro: levanta após `MAX_RETRIES` se content vazio/None/transiente persiste. `text` nunca `""` num retorno de sucesso.
- **`generate_json` → caller:** entrada `(prompt, task_type, retries, validate?)`; saída `dict | list` (JSON parseado e validado). Erro: `LLMJsonError` tipado após `retries` (carrega última `raw_text` + causa) — o worker converte em `AgentResult.fail`.
- **Worker → `generate_json`:** worker fornece `validate` opcional (ex.: carousel valida `"slides" in parsed` e contagem). Sem `validate`, só garante JSON bem-formado.
- **`_fail_job` → DB:** `generation_queue.status=failed` + `pipeline_status.error` + `content_ideas.status=pending WHERE status='processing'` (idempotente, guarded pelo status).

## Decisões de domínio

- **Content vazio é falha transiente, não erro do usuário.** Reasoning-only é probabilístico → retry é a resposta canônica (não trocar de modelo às cegas nesta RFC).
- **`_generate_sync` é a fonte única de retry de transporte.** Nenhum worker implementa seu próprio loop de retry de chamada; `generate_json` só retenta o ciclo parse (chamando `_generate_sync`, que já retenta transporte).
- **Parse+validação de JSON do LLM é responsabilidade do `generate_json`, não de cada worker.** Elimina a duplicação (DRY).
- **`retry_suggested`/`retry` do `AgentResult` deixa de ser o mecanismo de retry** — o retry acontece antes, dentro das camadas. O flag continua só pra sinalizar HTTP 503 em rotas de API.

## Edge cases sistêmicos

- **Content vazio persistente (grok "quebrado" N vezes seguidas):** após `retries` esgotados, `generate_json` levanta `LLMJsonError`; worker falha com `AgentResult.fail` e `_fail_job` reseta a idea pra `pending` (usuário pode retentar; não fica preso).
- **max_tokens vs reasoning:** carousel usa `max_tokens=3000`; reasoning-only observado ficou <3000 (não é truncamento por length). Fora de escopo mexer no valor — retry cobre.
- **Idempotência do reset:** `content_ideas` update é guarded por `WHERE status='processing'` — não sobrescreve idea que já avançou.
- **Rate limit (429):** ortogonal a esta RFC (limite 600/req/h por tenant no middleware). Retry desta RFC deve respeitar backoff pra não amplificar 429 — o retry vive dentro de `_generate_sync` (chamada ao provider, não ao próprio workers-API), então não conta no rate limiter interno.
- **JSON malformado ≠ vazio:** ambos tratados por `generate_json` (retry), mas logados distintos pra telemetria.

## Rollout / gate de deploy (obrigatório)

**Nada sobe em produção direto** (decisão Felipe, 24/07). Fluxo:

1. Implementar em branch (`feat/pdl-1522-*`), sem merge em `main`.
2. **Validar em preview/staging** dos workers — E2E real: disparar `pipeline/run` forçando content vazio (mock/seed) e confirmar retry + sucesso; confirmar reset de idea em falha persistente.
3. Só com **OK explícito do Felipe** após a validação → merge + deploy Coolify em prod.
4. ⚠️ **Aberto (item de plano):** `cadencia-workers` roda em Coolify/VPS Master, sem preview automático tipo Vercel. Definir com Infra o ambiente de validação (staging Coolify OU container efêmero OU teste local com mock do provider). Sem esse env definido, a Fatia 1 não pode ser validada fora de prod.

## Fora de escopo

- Trocar o modelo do task `carousel` (grok → outro) — decisão separada, dependente da telemetria que esta RFC instala.
- Desligar reasoning via params do provider — investigação futura (elo "aberto" do 5why).
- Rework do rate limiter (429) — issue própria.
- Mudar o contrato do `AgentResult` — mantido; só deixa de ser o ponto de retry.

## Regras resolvidas no grill

1. **1 RFC** (escopo focado num helper + guard; não fatiar em N).
2. Decisão central: **Opção C** (2 camadas, 2 fatias) — confirmada por Felipe 24/07.
3. Camada transporte trata content vazio; camada semântica trata parse+validação; workers só declaram `validate`.

## Alternativas consideradas

- **Opção A (só `_generate_sync`):** mínimo de código, mas retry "cego" sem contrato de JSON — não mata a duplicação de parse nos workers (DRY continua violado).
- **Opção B (só `generate_json`):** contrato explícito, mas deixa headline/caption/research (que também usam grok) sem o guard de transporte. Cobertura parcial.
- **C escolhida:** cobre transporte (todos) + semântica (JSON callers) sem sobreposição — ortogonal.

## Refs

- Issue: DEV-1522 · Incidente 5why: `pd-framework/incidents/2026-07-24_carousel-grok-content-vazio-parse-char0_5why.md`
- Incidente irmão: `pd-framework/incidents/2026-07-03_httpx-remoteprotocol-nao-retried-llm-ideas.md`
- Código: `cadencia-app/cadencia-workers/src/shared/llm.py` · `src/workers/carousel_agent/__init__.py` · `src/workers/orchestrator.py`
- Princípios: DRY (helper único) + Ortogonalidade (transporte vs semântica) + ETC (mudar tratamento de LLM fica local ao helper)
