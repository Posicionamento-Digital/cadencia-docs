---
type: source
source_kind: incidente
date: 2026-07-01
entities: ["[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-07-01_cadencia-playwright-timeout-google-fonts-cdn

# Incidente: Playwright timeout 15s no slide 1 — Google Fonts CDN externo bloqueia networkidle

**Data:** 01/07/2026
**Severidade:** Média
**Projeto:** Cadência (cadencia-workers)
**Duração do impacto:** Recorrente (intermitente — depende da latência da VPS ao Google CDN)
**Tags:** #backend #workers #conteudo #playwright #sentry #falha-detectada

## O que aconteceu

O Sentry gerou alertas recorrentes com:
> `Slide 1 render failed: Page.set_content: Timeout 15000ms exceeded.`

Ocorria durante o cron `/api/v1/cron/daily`, especificamente no slide 1 (capa) de carrosséis de tenants aleatórios. O pipeline de geração marcava o documento como `render_failed` e o usuário não via o carrossel.

## Causa raiz

**`cadencia-workers/src/workers/slide_renderer/__init__.py:2456` (antes da correção):**

```python
await page.set_content(slide_html, wait_until="networkidle", timeout=15000)
```

`wait_until="networkidle"` aguarda que não haja nenhuma conexão de rede aberta por 500ms. O CSS do tema injetado em cada slide (`theme_to_css()`) contém 7 presets com `@import url('https://fonts.googleapis.com/...')` em `theme_css.py` (linhas 456, 523, 576, 633, 682, 728, 815). No slide 1, o browser Chromium não tem cache e dispara downloads de 4-6 arquivos `.woff2` do `fonts.gstatic.com`. Com latência intermitente da VPS para a CDN do Google Fonts, o total de downloads ultrapassava 15s.

**Cadeia causal:**
1. Preset injeta `@import url(fonts.googleapis.com/...)` no CSS do tema
2. `theme_css` é injetado em todo slide antes do `page.set_content()`
3. Slide 1 não tem cache browser — Playwright inicia downloads de .woff2
4. VPS tem latência/bloqueio intermitente ao Google Fonts CDN
5. `networkidle` não dispara antes dos 15s
6. `TimeoutError` → slide 1 marcado como falho → documento sem carrossel

## Por que não foi detectado

- O timeout era intermitente (depende de condição de rede da VPS), não reproduzível localmente.
- Slides 2+ usavam o cache do browser criado no slide 1 — apenas o slide 1 era o gargalo.
- Não havia teste que mockasse latência de rede externa no render Playwright.
- O alerta Sentry existia mas era interpretado como falha esporádica, não como causa raiz sistêmica.

## Como foi corrigido

**slide_renderer**: Adicionada função `_inline_google_fonts(css: str) -> str` que:
1. Encontra todos `@import url('https://fonts.googleapis.com/...')` via regex
2. Para cada URL, busca o CSS com User-Agent Chrome (httpx síncrono) → obtém `@font-face` com URLs `.woff2`
3. Para cada `.woff2`, baixa o binário e converte para `data:font/woff2;base64,...`
4. Substitui o `@import` por `@font-face` inline — sem dependência de rede externa
5. Cacheia no dict de módulo `_FONT_CSS_CACHE` (uma busca por URL única por processo)
6. Fallback: se fetch falhar, mantém o `@import` original (degradação graciosa)

`wait_until="networkidle"` → `wait_until="load"` (fonts inline eliminam o bloqueador principal).
`PLAYWRIGHT_TIMEOUT` 15000 → 30000ms (defesa em profundidade para imagens Pexels CDN).

## Prevenção

### Checklist / regras pra evitar recorrência

- [x] `_inline_google_fonts()` executada sobre `theme_css` antes do loop Playwright em `render_slides()`
- [x] `test_playwright_timeout_is_30s`: quebra imediatamente se PLAYWRIGHT_TIMEOUT for reduzido de volta para 15s
- [x] `test_import_replaced_with_font_face_on_success`: verifica substituição real de @import por data URI
- [x] `test_import_kept_on_network_failure`: verifica fallback gracioso quando CDN falha
- [x] `test_result_cached_after_first_call`: verifica que httpx não é chamado duas vezes para a mesma URL
- [ ] Monitorar Sentry após deploy: se issue 7586124316 não reaparece, fix confirmado

### Pattern correto (renderer Playwright com recursos externos)

```python
# ERRADO — depende de CDN externo em produção:
await page.set_content(html_with_external_imports, wait_until="networkidle", timeout=15000)

# CORRETO — inline recursos antes de passar ao Playwright:
css = _inline_google_fonts(theme_css)   # elimina @import url(fonts.googleapis.com)
html = inject_css(template_html, css)
await page.set_content(html, wait_until="load", timeout=30000)
```

### Regra atualizada em

- [ ] CLAUDE.md do projeto (gotcha sobre render Playwright + CDN externo)
- [ ] Memória do agente — padrão "inline antes de renderizar"

## Commits relacionados

- `de9a6e8` — fix(workers): inline Google Fonts como data URI para evitar timeout Playwright (DEV-1021)
- `5518bc6` — fix(workers): warning quando woff2 não codificado no inline de fonts (P2 review)

## Links relacionados

- PR: https://github.com/felipeluissalgueiro/cadencia-app/pull/86
- Issue: DEV-1021 (maint: Cadência — Bugs e suporte)
- Sentry issue: 7586124316
- Incidente relacionado: `2026-07-01_cadencia-render-slides-ok-com-uploads-vazios-sentry-critical.md` (DEV-1022 — mesmo módulo, problema diferente)

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
