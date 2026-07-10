---
type: source
source_kind: incidente
date: 2026-05-29
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-05-29_cadencia-bugs-reais-growth-pipeline

# Incidente: Cadência growth pipeline — 3 bugs reais cross-tenant + 2 borderline descobertos no dogfooding

**Data:** 29/05/2026
**Severidade:** Alta
**Projeto:** Cadência (growth pipeline VPS Master + cadencia-workers)
**Duração do impacto:** PDL-355 e PDL-356 latentes desde inception do growth pipeline (~6 semanas, ~25/03 a 29/05). PDL-350 latente desde OpenAI descontinuar `dall-e-3` (data exata desconhecida — provavelmente 1-2 semanas). PDL-352 sempre existiu. PDL-351 sempre existiu.
**Tags:** `#backend` `#api` `#ghl` `#supabase` `#conteudo` `#silenciosa` `#regressao` `#falha-detectada`

> Recorte focado: este incidente cobre **apenas o que era bug ou design ruim do sistema**. Erros de configuração do provisioning manual + erros introduzidos durante os fixes estão registrados no incidente irmão `2026-05-29_cadencia-16-bugs-provisioning-tenant-felipe.md`.

## O que aconteceu

Felipe provisionou seu próprio tenant pessoal (`felipe@cadencia.ia.br`) como dogfood público (PDL-332). Ao testar o ciclo end-to-end com 10 ideias aprovadas em sequência, descobriu que **0 conteúdos foram gerados**. Investigação revelou que o sistema tinha múltiplas falhas reais — algumas silenciosas há semanas — que nenhum cliente havia exercitado completamente.

Cinco achados afetavam código de produção (não configuração de tenant):

1. **PDL-355 — Paginação `/contacts/` ausente.** Cron Seinfeld de TODOS os tenants disparava só pros 100 contatos mais recentes. Tenant com 7.614 contatos → 7.514 nunca receberam email Seinfeld.
2. **PDL-356 — Dedup Seinfeld não atômico.** Sistema marcava `seinfeld_sent=true` no post (post-level), não em `(post, contact, date)`. Retry/crash → contato recebia email 2x ou 3x.
3. **PDL-350 — `dall-e-3` descontinuado.** OpenAI removeu o modelo. `client.images.generate(model='dall-e-3')` retornava HTTP 400 em 100% das chamadas. Todo blog gerado nos últimos N dias saiu sem `featured_image_url`.
4. **PDL-352 — Mensagem de erro vaga.** `'ERROR: tenant is not on growth plan'` mascarava qual era o `plan_tier` atual vs esperado, onde estava sendo lido, e como consertar. Custo: tempo de debug. Não afetava clientes diretamente.
5. **PDL-351 — Cascade abort sem granularidade.** `trigger_server.py:run_pipeline` abortava TODO o pipeline (seinfeld + linkedin + instagram + newsletter) quando blog falhava. Comportamento existia por razão legítima (evitar dispatch de conteúdo de idea errada) mas não distinguia falha de validação/config (segura pra continuar) de falha mid-flight (não segura).

## Causa raiz

### PDL-355 — Paginação ausente
- **Arquivo:** `pipeline/seinfeld_generate.py:98-141` (e duplicado em `newsletter_generate.py:111`)
- **Bug:** função `get_all_contacts(location_id, api_key)` fazia 1 chamada GET pra `https://services.leadconnectorhq.com/contacts/?locationId=...&limit=100` e retornava o batch direto. Cursor `meta.startAfterId` + `meta.startAfter` documentado na GHL API V2 nunca foi implementado.
- **Impacto silencioso:** pipeline executava sem erro, log dizia "found N contacts" com N=100 honestamente, mas N não era o total. Para tenant com 100 contatos exatos: invisível. Para 7.614: 98.7% dos contatos órfãos.

### PDL-356 — Dedup não atômico
- **Arquivo:** `pipeline/seinfeld_generate.py` antes do fix
- **Bug:** após enviar email pro contato C do post P, sistema fazia `UPDATE published_posts SET seinfeld_sent=true WHERE id=P`. Flag binária post-level — não rastreava contato. Retry do mesmo job: 0 contatos identificados como já recebidos → todos recebem de novo.
- **Custo de não detecção:** baixo em condições normais (sem crash). Mas qualquer reset de cron, OOM kill, ou retry manual triplicava emails. Risco real de spam aos contatos dos tenants → reputação de domínio comprometida.

### PDL-350 — DALL-E 3 descontinuado
- **Arquivo:** `pipeline/blog_generate.py:207` + `pipeline/backfill_images.py:117`
- **Bug:** `model='dall-e-3'` hardcoded. OpenAI descontinuou em favor de `gpt-image-1` (mesmo modelo que `cadencia-workers/src/workers/cover_generation.py:250-294` já usa como fallback).
- **Detecção:** erro aparecia em `/cadencia/logs/trigger_server.log` como `ERROR: DALL-E 3 failed [BadRequestError]: 'dall-e-3' does not exist`, mas blog texto continuava sendo gerado OK (early return `return '', ''`) e `published_post` era criado sem `featured_image_url`. Frontend renderizava post sem cover. Tenants podiam confundir com bug de UX.

### PDL-352 — Mensagem vaga (DX, não funcional)
- **Arquivo:** `pipeline/blog_generate.py:265-266` antes do fix
- **Bug:** `print('ERROR: tenant is not on growth plan')` sem contexto. Quem investigasse esse erro precisava ler o código pra descobrir que o check era `config.get('plan_tier') != 'growth'` exato.
- **Não era bug funcional do produto** — era débito de observabilidade.

### PDL-351 — Cascade abort sem granularidade
- **Arquivo:** `pipeline/trigger_server.py:88-93` antes do fix
- **Comportamento:** `if code != 0: log("PIPELINE ABORTED"); return` após falha do blog. Pulava seinfeld + linkedin + instagram independente da causa da falha.
- **Por que existia:** legítimo proteger contra dispatch de conteúdo de idea errada. Se trigger é `idea_id=X` e blog X falhou, sem o `published_post` da idea X o seinfeld `--generate` pega o post mais antigo unscheduled e linkedin/instagram fazem fallback pra queue genérica → dispatch de idea Y pra um pedido de idea X.
- **Por que era ruim:** mesma regra valia pra trigger sem `idea_id` (cron normal / queue), onde não há "idea específica a preservar". Tratamento idêntico → over-blocking.

## Por que não foi detectado

### Causa transversal: falta de validação end-to-end com tenant real

Os 3 bugs reais (355/356/350) existiam há semanas em produção sem nenhum cliente exercitar o ciclo completo:

- **Tenants ativos** (CertaDoc/Fabiano + outros 9) usavam só subset das features. Nenhum tinha base de 7K+ contatos que expusesse PDL-355. Nenhum tinha cron Seinfeld rodando há semanas consecutivas com retries pra expor PDL-356. PDL-350 era novíssimo (OpenAI descontinuou recentemente).
- **Smoke tests existentes** eram unitários por componente — `blog_generate.py` rodava com `--dry-run` validando estrutura JSON, nunca exercitava a chamada real à OpenAI Images API.
- **Falhas silenciosas:** PDL-355 logava "Pagination done — 100 contacts" como sucesso; PDL-356 não logava nada; PDL-350 falhava mas `published_post` era criado normalmente.
- **Sem monitoring de outcomes:** ninguém media "X% dos blogs têm `featured_image_url IS NULL`" ou "tenant com Y contatos recebeu Z emails" pra cruzar.

### Causa específica: dogfooding pessoal

Quando Felipe provisionou tenant próprio, **3 dos bugs se tornaram visíveis em 1 sessão** porque o tenant dele tinha:
- Base GHL grande (7.614 contatos importados, expôs PDL-355)
- Vontade de gerar conteúdo nos 5 canais em sequência rápida (acelerou retry, mas PDL-356 não chegou a materializar antes do fix)
- Blog gerado mas sem cover visível (revelou PDL-350)

## Como foi corrigido

### PDL-355 — Paginação
- Commit `efc1394` (`cadencia-growth` main): `get_all_contacts` com cursor loop. Break em `not next_id`, `not next_ts`, `batch < batch_size`, ou cursor estagnado. Sleep 0.1s entre páginas.
- Aplicado em `seinfeld_generate.py` e `newsletter_generate.py`.
- Validação: smoke real contra location `PrAh9rKjmpUkElCu5KBI` → 76 páginas, 7.614/7.614 contatos em 42s.

### PDL-356 — Dedup atômico
- Commit `6da6b9d`: tabela `seinfeld_daily_sent` com `UNIQUE (tenant_id, contact_id, sent_date)`. INSERT atômico → conflict 409 = skip, 2xx = enviar, 4xx/5xx = pular sem enviar.
- Commit `77e70d9` (Claude P1+P2 reviews): `sb_insert` retorna 3 estados distintos (list OK, [] conflict, None erro). `sb_delete` real em rollback (não UPDATE sentinel 1970).
- Validação: INSERT/CONFLICT/DELETE/INSERT cycle real contra Supabase production — 6 PASS / 0 FAIL.

### PDL-350 — gpt-image-1
- Commit `5e66abf`: `model='gpt-image-1'`, `size='1536x1024'`, `quality='high'`, response em `b64_json` (sem download intermediário via URL).
- Commit `1f8f951` (Codex P1 + Claude P2 reviews): `base_url` explícito em `backfill_images.py` (evitar herdar `OPENAI_BASE_URL=openrouter.ai`); validação `b64_json` non-None antes de decode (mitiga moderação/policy refusal).
- Aplicado em `blog_generate.py:194-218` e `backfill_images.py:111-132`.
- Validação real em 30/05 02:07 UTC: 2 ideias aprovadas pelo Felipe → log mostrou `gpt-image-1 failed: Billing hard limit reached` (modelo correto sendo chamado; erro é billing OpenAI, externo ao código).

### PDL-352 — Mensagem estruturada
- Commit `5e66abf` (parte do mesmo): erro com `tier atual + esperado + source (tenant_config.config.plan_tier) + SQL fix copy-pastable`.
- Commit `1f8f951` (Claude P2 + Codex P2): `tenant_id` validado via `uuid.UUID()` antes de embebido em SQL exibido; SQL fix usa `config || jsonb_build_object(...)` (funciona com ou sem parent key blog).
- Validação real: rodada simulada na VPS com mock `plan_tier='growth_pro'` mostrou mensagem exata:
  ```
  ERROR: tenant 6bb2c1ba-... has plan_tier='growth_pro', expected 'growth'. Source: tenant_config.config.plan_tier. Fix: UPDATE tenant_config SET config = jsonb_set(config, '{plan_tier}', '"growth"') WHERE tenant_id = '6bb2c1ba-...';
  ```

### PDL-351 — Cascade condicional
- Commit `e030e3a` (após Codex P1 invalidar primeira tentativa simples): abort mantido só quando `content_idea_id` setado (idea-specific). Sem `content_idea_id` (cron/queue), pipeline segue independente.
- Razão Codex P1: opção B pura criaria regressão pior — seinfeld/linkedin/instagram fariam fallback pra queue genérica e dispatch-cariam ideia errada.
- Validação real em 30/05 02:07 UTC: blog falhou (billing OpenAI), pipeline NÃO abortou, seguiu pra `[seinfeld] starting` corretamente.

## Prevenção

### Checklist verificável

- [ ] **Antes de deploy de mudança em código de dispatch/scheduling:** rodar pipeline completo end-to-end com tenant real (não dry-run) + 1 contato real. Confirmar outcome esperado em banco + logs.
- [ ] **Antes de usar modelo OpenAI por nome:** consultar https://platform.openai.com/docs/models/overview e validar que o modelo está listado como `available`. Quando OpenAI descontinuar, capturar erro 400 com `code='model_not_found'` e logar como ALERT específico — não silencioso.
- [ ] **APIs com paginação cursor-based** (GHL, Stripe, etc): SEMPRE confirmar que loop está implementado lendo a documentação oficial, não confiar em "primeira página parece OK". Métrica: comparar count na 1ª chamada vs count total esperado (ex.: `/contacts/count` se existir).
- [ ] **Dedup em dispatch:** primary key composto via UNIQUE constraint no banco, não flag binária no objeto pai. INSERT atômico → conflict é skip seguro.
- [ ] **Mensagens de erro em validação de config:** SEMPRE incluir 4 campos: valor atual, valor esperado, fonte (tabela.campo), comando de fix (SQL/CLI/UI step).
- [ ] **Cascade aborts em pipelines:** distinguir falha de validação/config (recoverable em isolamento) de falha mid-flight (cascading). Em pipelines acionados por `idea_id`, abortar pra preservar invariante de "1 idea = 1 conjunto de outputs". Em pipelines de cron/queue, deixar cada channel decidir.
- [ ] **Monitoring de outcomes silenciosos:** dashboards de "% blogs com `featured_image_url IS NULL`", "% dispatches Seinfeld com count != esperado", "X contatos em base vs Y emails enviados" — pra capturar bugs silenciosos sem precisar de tenant exercitando ciclo completo.
- [ ] **Dogfood obrigatório pré-release:** próximo release significativo do growth pipeline deve ter Felipe (ou outro stakeholder) exercitar todos os canais end-to-end com tenant real ANTES do deploy.

### Pattern correto para os 3 padrões críticos

**Paginação cursor:**
```python
def get_all_contacts(location_id, api_key, batch_size=100):
    contacts = []
    cursor_id = None
    cursor_ts = None
    pages = 0
    while True:
        params = {"locationId": location_id, "limit": batch_size}
        if cursor_id: params["startAfterId"] = cursor_id
        if cursor_ts: params["startAfter"] = cursor_ts
        resp = ghl_request("GET", "/contacts/", api_key, params=params)
        batch = resp.get("contacts", [])
        if not batch: break
        contacts.extend(batch)
        meta = resp.get("meta", {})
        next_id = meta.get("startAfterId")
        next_ts = meta.get("startAfter")
        if not next_id or not next_ts: break
        if next_id == cursor_id: break  # cursor estagnado
        if len(batch) < batch_size: break
        cursor_id, cursor_ts = next_id, next_ts
        pages += 1
        time.sleep(0.1)
    return contacts
```

**Dedup atômico via UNIQUE:**
```sql
CREATE TABLE seinfeld_daily_sent (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    contact_id text NOT NULL,
    sent_date date NOT NULL,
    post_id uuid NOT NULL,
    sent_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, contact_id, sent_date)
);
```
```python
dedup_row = sb_insert('seinfeld_daily_sent', {...})
if dedup_row is None: continue  # erro técnico — NÃO envia
if dedup_row == []: continue    # conflict (já recebeu hoje) — NÃO envia
# Lista non-vazia — segue pro envio
```

**Mensagem de erro estruturada:**
```python
current_tier = config.get('plan_tier')
expected_tier = 'growth'
if current_tier != expected_tier:
    safe_tenant_id = str(uuid.UUID(str(tenant_id)))  # valida
    print(
        f'ERROR: tenant {safe_tenant_id} has plan_tier={current_tier!r}, '
        f'expected {expected_tier!r}. '
        f"Source: tenant_config.config.plan_tier. "
        f"Fix: UPDATE tenant_config SET config = jsonb_set(config, '{{plan_tier}}', '\"{expected_tier}\"') "
        f"WHERE tenant_id = '{safe_tenant_id}';"
    )
    sys.exit(1)
```

### Regra atualizada em

- [x] `pd-framework/times/produto/cadencia/memory/decisions.md` (4 entries no topo: PDL-353, 350+352, 351, 354 + 347+346)
- [x] `pd-framework/incidents/INDEX.md`
- [ ] Adicionar gotcha G019 em `EXPERTISE.md` — "dedup Seinfeld via Supabase, não GHL custom field"
- [ ] Adicionar gotcha G020 — "OpenAI image gen sempre `gpt-image-1`, nunca `dall-e-3`"
- [ ] Adicionar gotcha G021 — "GHL `/contacts/` exige cursor `startAfterId + startAfter` pra paginar além de 100"

## Commits relacionados

Repo `Posicionamento-Digital/cadencia-growth`, branch `main`:

- `efc1394` — fix(pagination): get_all_contacts pagina todos contatos via meta.startAfterId (PDL-355)
- `6da6b9d` — fix(dedup): seinfeld dispatch usa seinfeld_daily_sent com UNIQUE constraint (PDL-356)
- `5ade215` — fix(dedup): define helper sb_insert (Codex P1 PDL-356)
- `77e70d9` — fix(dedup): sb_insert 3-estados + sb_delete rollback real (Claude P1+P2 PDL-356)
- `e95da5a` — docs: runtime-fix-review PDL-355+356 (6 PASS / 0 FAIL real Supabase)
- `5e66abf` — fix(images,errors): gpt-image-1 + erro plan_tier estruturado (PDL-350 + PDL-352)
- `1f8f951` — fix(images,errors): P1+P2 reviews (base_url, b64decode, SQL injection, jsonb_set)
- `438254f` — fix(pipeline): channels independentes (PDL-351, opção B inicial)
- `e030e3a` — fix(pipeline): abort só em idea-specific (PDL-351 Codex P1 fix)

## Links relacionados

- Incidente irmão (escopo amplo): `pd-framework/incidents/2026-05-29_cadencia-16-bugs-provisioning-tenant-felipe.md`
- Reports de review: `cadencia-growth/docs/{codex,claude,runtime}-reviews/*-pdl{350,351,352,355,356}.md`
- Decisões: `pd-framework/times/produto/cadencia/memory/decisions.md` (entries 2026-05-29 e 2026-05-30)
- Linear PDLs: 350, 351, 352, 355, 356 — todas em `Done`
- VPS Master backup: `/cadencia/pipeline/{blog_generate,backfill_images,trigger_server,seinfeld_generate,newsletter_generate}.py.bak-pdl*`

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
