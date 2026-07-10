> **📄 Cópia local — fonte de verdade no GitHub.**
> Origem: [`felipeluissalgueiro/cadencia-app` / `master` / `docs/adr/0005-location-pit-token-por-tenant.md`](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0005-location-pit-token-por-tenant.md)
> Sincronizar via `/documentar` ou `sync_to_framework.py`.

---

# ADR-0005 — `location_pit_token` por tenant (não global)

**Status:** aceito · **Data:** 2026-05-27

## Contexto

GHL oferece dois tipos de token:

1. **`api_key`** — antigo, global por subconta. Permissões amplas, mas perde sessão e tem rate limit por key.
2. **`location_pit_token`** (Private Integration Token) — token de location específica. Permissões controláveis, mais novo, recomendado pela GHL.

Endpoints críticos do Cadência (seinfeld dispatch, scoring webhook, contatos) precisam autenticar **como o tenant**, na subconta do tenant.

## Decisão

Cada tenant tem seu próprio `config.ghl.location_pit_token` em `tenant_config`. Gerado durante provisioning via `POST /oauth/locationToken` (que exige `ghl_agency_oauth` válido).

Os seguintes scripts/workers usam `location_pit_token`:

- `/cadencia/pipeline/seinfeld_generate.py` (dispatch)
- `/cadencia/scoring/webhook_handler.py`
- `/cadencia/pipeline/newsletter_generate.py`

A location central da Cadência (`PrAh9rKjmpUkElCu5KBI`) tem **token global** (`GHL_API_KEY` env) usado apenas pelos workers do `cadencia-app` (`integrations/ghl.py`) para tracking lifecycle dos próprios clientes — não para conteúdo de tenant.

## Consequências

- ✅ Isolamento real — vazamento do token de um tenant não compromete outros.
- ✅ Permissões granulares — cada token só acessa sua location.
- ✅ Conformidade com modelo recomendado pela GHL.
- ❌ Provisioning depende de `ghl_agency_oauth` válido — hoje vazio (PDL-25). Sem isso, token não é gerado automaticamente.
- ❌ Confusão comum: "GHL no workers usa token global" (sim, mas só para tracking da Cadência) vs "GHL no growth usa token do tenant" (G004 + G007).

## Não considerado

- `api_key` global por subconta — descontinuação anunciada pela GHL, permissões grosseiras.
- Token único compartilhado — perde isolamento entre tenants.

## Referências

- `times/produto/cadencia/context/how-it-works.md` — seção "Email Seinfeld" e "Scoring de leads"
- Gotchas G004, G007 em `times/produto/cadencia/CLAUDE.md`
