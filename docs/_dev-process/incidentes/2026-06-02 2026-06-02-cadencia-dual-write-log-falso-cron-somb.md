---
type: source
source_kind: incidente
date: 2026-06-02
entities: ["[[Cadencia]]"]
tags: [incidente, wiki-backfill]
moc: "[[MOC-Projetos]]"
generated: wiki-backfill
---
# 2026-06-02_cadencia-dual-write-log-falso-cron-sombra-timeout-dispatch

# 2026-06-02 — Cadência: dual-write de log fez parecer que existia "cron sombra"; causa raiz da triplicação histórica era timeout do dispatch

**Projeto:** Cadência (growth pipeline)
**Severidade:** Média
**Tags:** `#backend` `#cron` `#silenciosa` `#regressao` `#log` `#observabilidade`

---

## Resumo

O log `/cadencia/logs/growth_pipeline.log` mostrava o header `growth_pipeline START` aparecendo 2× com timestamp idêntico ao microssegundo em todo dia útil desde pelo menos 25/05. Felipe havia relatado triplicação histórica de envios de email Seinfeld para os mesmos contatos. Hipótese inicial: cron sombra disparando o pipeline em paralelo.

**Diagnóstico Pólya confirmou:** o cron sempre rodou 1×/dia. O header aparecia 2× porque `growth_pipeline.py` faz `print(header)` + `f.write(header)` para o mesmo arquivo (cron redireciona `>> log 2>&1`), gerando dual-write. Mesma string, mesmo `now.isoformat()`, mesmo arquivo.

A **triplicação real** de envios era sintoma de outro bug, **não** de cron duplicado: `seinfeld_generate.py --dispatch` ultrapassa os 300s de timeout do orquestrador em tenants grandes (Felipe = 7618 contatos GHL), subprocess morre, `published_posts.seinfeld_sent` permanece `false`, próxima execução re-roda envio. Sem `seinfeld_daily_sent` (PDL-356, recente), não havia barreira de dedup — cada retry duplicava/triplicava.

## Linha do tempo

- **02/06 ~14:00 UTC** — Cron diário roda, dispatch do Felipe estoura 300s (timeout). Email do dia 02/06 não saiu. Posts continuam `seinfeld_sent=false`.
- **02/06 ~19h BRT** — Felipe traz bug report (`bug-growth-pipeline-silencioso.md`) e pede investigação.
- **02/06 ~22h BRT** — Investigação Pólya identifica dual-write + timeout como causas. Fixes aplicados, dispatch perdido re-disparado em background.

## Achados detalhados

1. **Dual-write log (cosmético, mas confunde diagnóstico):**
   - `growth_pipeline.py:122-125` e `:210-213`: `print(header)` + `f.write(header)` (idem footer).
   - Cron tem `>> /cadencia/logs/growth_pipeline.log 2>&1` — stdout vai parar no mesmo arquivo.
   - `journalctl` mostra **1** invocação por dia (PID único).

2. **Timeout dispatch (causa raiz operacional):**
   - `run_script()` hardcoded `timeout=300`.
   - Tenant Felipe: 7618 contatos × envio síncrono via GHL `/conversations/messages` (~100-300ms cada, sem paralelismo) + paginação inicial (~76 requests × 0.1s sleep + latência) → impossível em 5 min.
   - Subprocess killed pelo orquestrador → `seinfeld_sent` não marcado → re-tentativa no dia seguinte (mesmo dia se cron rodasse de novo).

3. **Triplicação histórica explicada:** antes de PDL-356, qualquer retry pós-timeout reenviava os contatos já alcançados, sem dedup. Combinava com timeouts repetidos = triplicação. Hoje há barreira `UNIQUE (tenant_id, contact_id, sent_date)` em `seinfeld_daily_sent` que segura o problema **na borda do banco** — 0 duplicados em 418 envios confirmados.

4. **Hipótese descartada (cron sombra):**
   - `/etc/crontab`, `/etc/cron.d/`, `/etc/cron.daily/`, `/etc/cron.hourly/`: nenhuma referência ao pipeline.
   - `crontab -u root`: 1 entrada `0 14 * * * /usr/bin/python3 /cadencia/crons/growth_pipeline.py sync blog seinfeld linkedin instagram`.
   - `systemd list-timers`: nenhum timer relacionado.
   - `trigger_server.py`: endpoints `_handle_newsletter` / `_handle_provision` — não há rota que dispare o pipeline diário completo.

## Fix aplicado

**Arquivo:** `/cadencia/crons/growth_pipeline.py` (backup `growth_pipeline.py.bak-pdl361-20260602-2225`)

1. `run_script(..., timeout=300)` — parâmetro com default retrocompatível.
2. Loop principal: `step_timeout = 1800 if (script == 'seinfeld_generate.py' and '--dispatch' in extra_args) else 300`.
3. Removido `f.write(header)` / `f.write(footer)` — single-write via `print()`. Cron continua persistindo via redirect; execução manual mostra no terminal.

Compile check remoto OK.

**Ação manual:** re-disparado `seinfeld_generate.py 6bb2c1ba --dispatch` em background na VPS Master para recuperar o envio perdido de 02/06 (não tinha sido enviado por causa do timeout do cron 14:00).

## Prevenção

- **Não duplicar streams de log no mesmo destino.** Se cron redireciona stdout para o log, o script não deve escrever no mesmo arquivo manualmente. Hoje sobrou em outros pontos? Auditar outros scripts com mesmo padrão.
- **Timeout do orquestrador deve ser função do tamanho da tarefa.** Operações que escalam com base de contatos não podem ter timeout fixo igual a operações com `--generate` (que tocam 1 post).
- **Hipótese de "dispatch duplicado" sempre exige `journalctl` + contagem de PIDs antes de gastar ciclos.** O log do app é fonte secundária.

## Pendências relacionadas (não resolvidas neste incidente)

- **P4 — Tenant 91694c2d (Lab. Crescimento)**: `provisioning_status=partial`, `GHL create_location 403 Forbidden`. Causa: `GHL_AGENCY_TOKEN` (fallback estático) sem scope `locations/write`. Resolução: rotacionar PIT Agency com scope correto (1P) ou criar sub-account manualmente.
- **Otimização dispatch tenants grandes**: 1800s ganha tempo, não escala. Próxima evolução é paralelizar envios ou mover dispatch para fila.

## Detecção futura

Adicionar no `trigger_server.py /status` ou em healthcheck:
- alerta se `seinfeld_scheduled_at::date < hoje` AND `seinfeld_sent=false` (envio agendado e não cumprido).
- alerta se runtime do `--dispatch` > 80% do timeout configurado.
