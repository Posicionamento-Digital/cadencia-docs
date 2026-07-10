---
type: source
source_kind: incidente
date: 2026-06-10
entities: ["[[Cadencia-Growth]]", "[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-10_cadencia-generation-queue-4-defeitos-design-despacho

# Incidente: generation_queue — 4 defeitos de design no despacho convergindo em blogs duplicados, carrosséis faltando e órfãs

**Data:** 10/06/2026
**Severidade:** Alta
**Projeto:** Cadência
**Duração do impacto:** desde ~abril (race condition documentada em 25/04) até 10/06; sintomas agudos no tenant Alexandre em 09/06
**Tags:** `#backend` `#bd` `#supabase` `#railway` `#vps` `#schema-drift` `#silenciosa` `#regressao` `#conteudo`

## O que aconteceu

Investigação estruturada (/debug-polya, modo CRÍTICO) do PDL-171 revelou que os bugs recorrentes do `generation_queue` (PDL-470, 473, 476, 477, 478) não eram bugs isolados — eram 4 defeitos de design na mesma arquitetura de despacho:

1. **Aprovação = 3 dispatches fire-and-forget** (`/pipeline/run` Railway + insert `generation_queue` + `trigger-generation` VPS), todos com `.catch(() => {})` — erros engolidos, sem reconciliação. Na rajada de 8 swipes do tenant Alexandre (09/06 17:11), 6 chamadas ao Railway falharam silenciosamente → 6 de 8 posts sem carrossel (PDL-473).
2. **Row de bookkeeping nascia `pending` sem consumidor** — o despacho real vai por HTTP body (direct mode); a coluna `channels` era write-only. Órfãs acumulavam pra sempre (PDL-470).
3. **Cron diário (11h BRT) consumia qualquer row pending sem filtro de canal nem dedupe** — pegava a órfã da aprovação e gerava o MESMO blog de novo (3 pares duplicados confirmados no tenant felipe-salgueiro: 29/05, 03/06, 08-09/06). `trigger_server.py` ainda spawnava 1 thread por trigger sem lock — 8 pipelines paralelos no mesmo tenant.
4. **Schema drift desde abril:** `channel` e `topic` existiam em prod sem migration versionada; a migration de 02/06 (`channels[]`) atacou só o sintoma do insert.

Agravante: em 09/06 um agente sem supervisão "corrigiu" marcando as 9 órfãs do Alexandre como `completed` em lote (22:15) — destruiu a evidência sem corrigir nada e sem logar a sessão.

## Causa raiz

A `generation_queue` nasceu pro carrossel Railway; o Growth foi pendurado nela em abril, gerou race condition (incidente 25/04), e o "fix" foi bypass (direct mode `--idea-id`) **deixando a fila semanticamente quebrada**. Cada sintoma posterior ganhou patch isolado; os 4 defeitos estruturais continuaram gerando bugs novos a cada semana. A prevenção do incidente de 25/04 já avisava: "qualquer pipeline VPS que dependa de generation_queue deve usar passagem direta de ID, não polling" — mas o modo fila do cron ficou ativo, sem filtro e sem dedupe.

## Por que não foi detectado

- 3 dispatches fire-and-forget com `.catch(() => {})` — nenhum erro visível no frontend
- Railway/VPS logam mas não propagam; "completed" aparentava sucesso
- Duplicatas de blog só visíveis comparando `published_posts` por `content_idea_id`/título
- Limpezas manuais (inclusive por agente não supervisionado) mascaravam o acúmulo de órfãs

## Como foi corrigido

Branch `felipeluissalgueiro/pdl-171-fix-definitivo-generation-queue` (cadencia-app) + deploy direto na VPS Master (backup `.bak-20260610-2049`):

1. **`generation-queue/route.ts`**: insert com `status='dispatched'` (registro, não fila) — mata órfãs na raiz; bônus: `usePipelineStatus` para de pollar eternamente
2. **`blog_generate.py`** (VPS): dedupe por `content_idea_id` em `published_posts` (ambos os modos) + filtro `channels=cs.%7Bblog%7D` no modo fila (URL-encoded — `sb_get` usa curl, que globba `{}`)
3. **`trigger_server.py`** (VPS): `run_pipeline_locked` — lock por tenant serializa pipelines do mesmo tenant
4. **Migration `20260610210000`**: versiona `channel`/`topic` + índice (aplicada em prod via Management API)
5. **DML**: 2 rows zumbis `processing` (tenants showcase, crons Railway mortos no meio) → `failed`
6. Cópia `cadencia-growth/` do monorepo sincronizada com a VPS (estava stale)

E2E validado em prod: dedupe SKIP em direct e queue mode; filtro de canal funcionando; `cadencia-trigger.service` ativo.

## Prevenção

### Checklist / regras pra evitar recorrência

- [ ] Consumidor de `generation_queue` SEMPRE filtra canal — nunca pegar row que não é dele
- [ ] Qualquer caminho novo de geração de blog preserva o dedupe por `content_idea_id`
- [ ] Coluna nova em prod = migration versionada no mesmo dia (critério: `pg_dump --schema-only == migrations`)
- [ ] Operador PostgREST com `{}` via `sb_get`/curl: URL-encodar (`%7B...%7D`) — curl globba chaves
- [ ] Agente que mutar dados em prod: registrar sessão (log) + issue — limpeza sem rastro destrói evidência
- [ ] Pendências estruturais de incidente (como o de 25/04) viram issue própria — bypass não fecha causa raiz

### Follow-ups abertos

- PDL-168 — endpoint atômico approve+enqueue (mata o fire-and-forget triplo)
- PDL-167 — watchdog/cron pra rows `processing`/órfãs velhas
- PDL-476/477/478 — flags de bookkeeping (`linkedin_sent`, `newsletter_included`, contagem do front)
- PDL-213 — separar `cadencia-growth` em repo próprio (VPS sem git é o que permitiu o drift monorepo×VPS)

## Commits relacionados

- `d4c6566` (cadencia-app, branch pdl-171) — fix definitivo generation_queue

---
*Registrado via sistema de incidentes. Ver INDEX.md para histórico completo.*
