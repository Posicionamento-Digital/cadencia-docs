---
type: source
source_kind: incidente
date: 2026-07-01
entities: ["[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-07-01_cadencia-render-slides-ok-com-uploads-vazios-sentry-critical

# render_slides() retornava ok() com png_urls vazios quando Storage falha — CRITICAL Sentry

**Data:** 2026-07-01
**Severidade:** Média
**Projeto:** Cadência (cadencia-workers)
**Duração:** Recorrente (múltiplos docs afetados, ex: f0cfecea-8348-49c3-b0d1-6f94d80141a2)
**Tags:** #backend #supabase #workers #conteudo #falha-detectada #sentry

## O que aconteceu

O Sentry gerou alert CRITICAL recorrente com a mensagem:
> `CRITICAL: slides_content written but URL missing on re-read for doc <uuid>`

Documentos de carrossel eram marcados como `render_failed` pelo sistema de verificação do orchestrator, bloqueando usuários de ver seus carrosséis. O alert era gerado pelo cron `/api/v1/cron/daily` durante a geração de carrosséis.

## Causa raiz

**`cadencia-workers/src/workers/slide_renderer/__init__.py` (antes da linha 2490):**

`render_slides()` retornava `AgentResult.ok({"png_urls": ["", ""]})` mesmo quando **todos** os uploads para o Supabase Storage falhavam (após 3 retries + HEAD fallback). O tratamento de upload falho era: `png_urls.append("")` — não-fatal, sem `fail()`.

No orchestrator, o merge loop `if i < len(png_urls) and png_urls[i]:` saltava entradas vazias, então nenhum slide recebia `url`. A escrita no banco ficava sem URLs. A query de verificação `select("slides_content->0->url")` detectava isso e disparava o CRITICAL.

**Causa secundária — `cadencia-workers/src/workers/orchestrator.py:799`:**

A query de verificação usava PostgREST JSON path `select("slides_content->0->url")` + `verify.data.get("url")`. O alias de coluna retornado por PostgREST para paths JSON varia entre versões, podendo gerar falsos positivos onde a URL existe no banco mas `verify.data.get("url")` retorna None.

## Por que não foi detectado

- `render_slides()` tinha tratamento correto para falha catastrófica (Playwright crash → `fail()`) mas não para falha silenciosa de Storage (todos uploads retornam `""` → `ok()` com lista vazia).
- O guard de verificação no orchestrator (adicionado em CAD-671) detectou o problema corretamente, mas o log CRITICAL gerava Sentry alert mesmo sendo o comportamento **esperado** para falha de Storage.
- Os testes do orchestrator não cobriam o cenário `render_slides()` → `ok()` com png_urls vazios.

## Como foi corrigido

**slide_renderer**: Após o loop de rendering, verifica `uploaded_count = len([u for u in png_urls if u])`. Se `png_urls and uploaded_count == 0`, retorna `AgentResult.fail("All N slide uploads failed — Supabase Storage may be unavailable", retry=True)`. Isso faz o orchestrator seguir o path `render_failed` limpo que já existia (sem CRITICAL log).

**orchestrator**: Query de verificação migrada de `select("slides_content->0->url")` para `select("slides_content")` com inspeção em Python: `_slides_verified[0].get("url")`. Elimina dependência de alias de coluna PostgREST. Log de erro inclui `slides_count` e `first_keys` para diagnóstico futuro.

**tests**: Mock de `content_documents` select atualizado com `side_effect` por coluna selecionada (retorna `slides_content` real quando pedido, `status` quando pedido status). Corrigiu 7 falhas pré-existentes no mock onde `data=[{}]` (lista) era retornado onde `maybe_single()` esperava dict ou None. 2 novos testes adicionados.

## Prevenção

- [x] **Teste `test_pipeline_marks_render_failed_when_all_uploads_fail`**: verifica que orchestrator marca `render_failed` quando `render_slides()` reporta falha total de uploads.
- [x] **Teste `test_pipeline_url_verify_uses_slides_content_field`**: verifica que a verificação detecta slide sem URL via `slides_content` direto.
- [ ] **Monitorar Sentry após deploy**: se o alert DEV-1022 não reaparece após deploy em Coolify, fix confirmado.
- [ ] **Investigar causa raiz do Storage falhar**: o retry de 3x + HEAD fallback já existe. Se continuar falhando periodicamente, investigar rate limit ou timeout de Storage do Supabase.

### Pattern correto (verificação de URL pós-escrita)
```python
# ERRADO (alias PostgREST pode variar):
verify = sb.table("content_documents").select("slides_content->0->url").eq("id", doc_id).single().execute()
if verify.data and not verify.data.get("url"):

# CORRETO (leitura direta + parse Python):
verify = sb.table("content_documents").select("slides_content").eq("id", doc_id).single().execute()
_slides = (verify.data or {}).get("slides_content") or []
_first_url = _slides[0].get("url") if _slides else None
if not _first_url:
```

### Pattern correto (render_slides com falha total de Storage)
```python
uploaded_count = len([u for u in png_urls if u])
if png_urls and uploaded_count == 0:
    return AgentResult.fail(
        f"All {len(png_urls)} slide uploads failed — Supabase Storage may be unavailable",
        retry=True,
    )
```

## Commits relacionados

- `9663555` — fix(workers): evita CRITICAL Sentry ao detectar falha total de upload de slides (DEV-1022)

## Links relacionados

- Issue: DEV-1022 (maint: Cadência — Bugs e suporte)
- Sentry issue: 7586125061
- PR: https://github.com/felipeluissalgueiro/cadencia-app/pull/85
- Incidente relacionado: `2026-06-29_llm-finish-reason-error-nao-retentava.md` (mesmo padrão: retorno silencioso ok() em erro transiente)
