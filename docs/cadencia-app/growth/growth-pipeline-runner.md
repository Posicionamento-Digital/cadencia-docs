# growth-pipeline-runner — cron diário + trigger on-demand

## TL;DR

2 servidores na VPS Master que disparam a geração de conteúdo: `growth_pipeline.py` (cron diário para todos os tenants) e `trigger_server.py` (HTTP on-demand por tenant).

## Identidade

- **Tipo:** Python scripts (systemd / cron)
- **Paths (VPS `/cadencia/`):**
  - `crons/growth_pipeline.py` — runner batch diário
  - `pipeline/trigger_server.py` — servidor HTTP porta 39090
- **Status:** ativo em produção
- **Deps:** Todos os scripts de geração (seinfeld, blog, linkedin, etc.)

## growth_pipeline.py (cron diário)

- **Schedule:** `0 14 * * *` UTC (11h BRT) — sync + blog + seinfeld + linkedin + instagram
- **Schedule:** `0 18 * * 5` UTC (15h BRT sexta) — newsletter semanal
- `get_growth_tenants()`: busca TODOS os tenants com config — sem filtro de plano ou onboarding
- Verifica créditos: se tenant sem créditos → skip (exceto sync + newsletter)
- Planos `trial`/`essencial`/`starter`: blog/linkedin/instagram só seg e qui (weekday 0 e 3), sem seinfeld diário
- Ordem: sync → blog → seinfeld `--generate` → seinfeld `--dispatch` → newsletter → linkedin → instagram

## trigger_server.py (on-demand)

- **Porta:** 39090 (reboot automático via @reboot cron)
- Endpoints: `POST /trigger`, `POST /provision`, `POST /newsletter`, `GET /status`
- `/trigger` executa em thread separada: sync → blog → seinfeld `--generate` → linkedin → instagram
- Newsletter **explicitamente pulada** no trigger on-demand (só roda pelo cron sexta); se `channels` incluir `newsletter`, o 202 devolve `warnings` avisando o motivo (DEV-496/G002) — antes ficava silencioso
- Se blog falha → abort (não roda seinfeld/linkedin com conteúdo stale)

## Fluxo carrossel/reels (NÃO passa aqui)

```
Scheduler externo (disparador não confirmado — ver Foundation - Tech Architecture §Cron jobs)
  → POST /api/app/trigger-generation (Vercel)
  ↓
Vercel filtra carrossel/reels → workers Coolify VPS Master
VPS: recebe APENAS blog/seinfeld/linkedin/instagram
```

## Gotchas

- G005: processa TODOS os tenants — sem filtro onboarding_completed
- G006: trial/essencial não recebem seinfeld, só 2x/sem os outros
- Newsletter nunca roda no trigger on-demand (G002)
- **Gate por provider (DEV-1040):** o runner valida somente a configuração do
  canal solicitado. Email/newsletter usam Resend e contatos do CRM; LinkedIn e
  Instagram usam suas integrações próprias. Espelha o gate de
  `trigger-generation/route.ts` (cadencia-app).

---

## Quando usar

- **Cron 11h BRT VPS**: pipeline diário automático (`growth_pipeline.py sync blog seinfeld linkedin instagram`).
- **Cron sexta 15h BRT**: newsletter semanal (`growth_pipeline.py newsletter`).
- **On-demand**: `trigger_server.py` chama `run_pipeline()` quando usuário aprova ideia (filtra carrossel/reels que vão para os workers Coolify VPS Master).
- **Retry**: catch-up de tenants com `provisioning_status='failed'` via `retry_provisioning.py` (10h55 BRT).

## Quando NÃO usar

- ❌ Para gerar **carrossel** ou **reels** — esses não rodam aqui. Ver [ADR-0004](../docs/adr/0004-carrossel-railway-resto-vps.md).
- ❌ Como sistema de filas confiável — não tem retry/backoff robusto; falhas críticas exigem registro de incident.
- ❌ Para testar geração de UM tenant — usar script Python direto chamando `seinfeld_generate.py --tenant <id>`.

## Por que funciona assim

- [ADR-0004](../docs/adr/0004-carrossel-railway-resto-vps.md) — Carrossel/reels Railway, blog/seinfeld/etc VPS.
- Cron diário fixo (não fila persistente) — simplicidade operacional. Trade-off: se VPS cair, posts do dia perdidos.
- `get_growth_tenants()` retorna **todos** os tenants com config — sem filtro `onboarding_completed` (G005). Decisão: melhor gerar e ter post extra do que tenant esquecido.

## 🚫 Don'ts

- **Não** rodar `growth_pipeline.py` sem `--tenant` em produção fora do cron — gera para TODOS, custo LLM explode.
- **Não** adicionar canal novo sem alinhar com `trigger_server.py` (lista de canais filtrados).
- **Não** ignorar tenants `trial`/`essencial` — eles também recebem blog/linkedin/instagram (só em seg+qui).
- **Não** silenciar erro de step — pipeline mascara falha cascateada (blog falha → seinfeld gera com conteúdo stale).

## 🪦 Já tentamos

- **2026-04-16 — Railway seinfeld cron parou 2 dias**: cron na Railway falhou silenciosamente. Migrou para VPS. Ver `2026-04-16_railway-seinfeld-cron-parou-2-dias.md`.
- **2026-04-17 — Cron newsletter desapareceu VPS**: crontab perdeu entrada após reboot. Fix: backup do crontab. Ver `2026-04-17_cron-newsletter-desapareceu-vps.md`.
- **2026-04-17 — Crons newsletter+seinfeld não dispararam**: timezone do cron BRT vs UTC. Ver `2026-04-17_crons-newsletter-seinfeld-nao-dispararam-vps.md`.
- **2026-04-26 — Trigger secret mismatch**: env var no Vercel tinha trailing newline. Pipeline silenciosa. Ver `2026-04-26_trigger-secret-mismatch-pipeline-silenciosa.md`.
- **2026-04-21 — Disparo blog hang sem timeout subprocess**: blog travou e bloqueou seinfeld/linkedin. Ver `2026-04-21_disparo-blog-hang-sem-timeout-subprocess.md`.

## 🔥 Troubleshooting

| Sintoma | Causa provável | Fix |
|---|---|---|
| Cron não rodou | Crontab perdido ou timezone errado | `crontab -l`; reconciliar com `_core/VPS-ACCESS.md` |
| Pipeline trava em step | Subprocess sem timeout | Adicionar `timeout=N` em todos `subprocess.run` |
| Tenant não gerou | Sem créditos OU sem `tenant_config` | `SELECT * FROM tenant_plans WHERE tenant_id=X AND status='active'` |
| Newsletter rodou no trigger | NÃO deveria — está pulada (G002) | Verificar log `run_pipeline()` |
| Step blog falha → resto roda mesmo assim | Abort não propaga | Forçar abort no `run_pipeline()` quando blog falha |

## 📚 Referências cruzadas

- [seinfeld-email](seinfeld-email.md)
- [newsletter](newsletter.md)
- [linkedin-generation](linkedin-generation.md)
- [blog-instagram-gen](blog-instagram-gen.md)
- [scoring-leads](scoring-leads.md)
- ADR: [0004 Railway/VPS](https://github.com/felipeluissalgueiro/cadencia-app/blob/master/docs/adr/0004-carrossel-railway-resto-vps.md)
