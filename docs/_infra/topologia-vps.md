# Topologia VPS — Squad Infra

> Snapshot do estado real das VPS PD em 2026-05-25. Refresh recomendado mensal ou após mudança grande de infra. Fonte completa: `docs/snapshots/vps-{master,dev}-2026-05-25.md`.

---

## VPS Master — produção (72.60.4.71)

**Acesso:** `ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71`
**Skill:** `/vps-master`
**Sistema:** Ubuntu (Hostinger)
**User:** `master` (sudo OK)

### Containers Docker (17, todos healthy 2+ dias)

| Categoria | Containers | Observação |
|---|---|---|
| Coolify stack | coolify, coolify-sentinel, coolify-proxy (traefik v3.3.5), coolify-db (pg15), coolify-redis, coolify-realtime | Core do deploy |
| CS / Lara | lara-ceilandia, lara-central | Image `openclaw-openclaw` — image base mantida mesmo após depreciar OpenClaw comercial |
| GCI Ecuro | ecuromiddleware-middleware-1, ecuromiddleware-ecuro-postgres-1, ecuromiddleware-postgres-1 | Cliente GCI-GO |
| Cadência | cadencia-postgres (pg16), cadencia-redis, cadencia-redis-db, cadencia-n8n-main, cadencia-n8n-worker-1, cadencia-n8n-runner-worker-1 | Produto core |

### Systemd services customizados (rodando)

| Service | Função | Path |
|---|---|---|
| `grafana-webhook.service` | Webhook v2 Grafana → WhatsApp + Linear (com dedup fingerprint) | `/opt/grafana-webhook` (porta 9300) |
| `cadencia-webhook.service` | Cadencia Growth Scoring Webhook Handler | (no monorepo Cadência) |
| `scoring-webhook.service` | Scoring Webhook Handler — PD Marketing (origem GHL — **legado em desligamento**; scoring migra p/ webhook Resend do CRM Cadencia, ver `_core/GHL-TO-CADENCIA-MIGRATION.md`) | (`/root/pd-marketing/` ou similar) |
| `stamper-bot.service` | Stamper Telegram Bot (Claude-powered) | `/opt/stamper-telegram-bot` |

Nativos: alloy (Grafana agent), netdata, cloudflared, monarx-agent (security scanner Hostinger), containerd.

### /opt/ — projetos

| Pasta | Owner | Mod | Destino no framework |
|---|---|---|---|
| `assessoria-imprensa-cadencia` | master | 2026-05-05 | `times/produto/ferramentas-ia/cadencia/times/growth/` (componente) |
| `cadencia-app` | master | 2026-05-20 | `times/produto/ferramentas-ia/cadencia/times/frontend/` (deploy artifact) |
| `grafana-webhook` | master | 2026-05-24 | `times/infra/workers/webhook-receptor/` (PDL-223 migra) |
| `insight-artificial` | master | 2026-05-22 | `times/marketing/workers/insight-artificial/` |
| `lara-ai` | master | 2026-05-19 | `times/produto/gci-go/components/lara/` |
| `openclaw` | master | 2026-04-21 | `_archive/openclaw/` — uso comercial PD depreciar (image Lara mantém) |
| `scripts` | root | 2026-05-24 | `times/infra/runbooks/legacy/` + `workers/legacy/` |
| `stamper-telegram-bot` | master | 2026-05-20 | `stamper/bot-telegram/` (Fase 1 decide se mantém) |

### Crontab ROOT — 38 entries (categorias)

**pd-marketing (15+ entries — vive em `/root/pd-marketing/`, a mover pra `/opt/apps/`):**
- `disparo-seinfeld.py` (14h), `disparo-ideacao.py` (05h), `disparo-blog.py` (00h + 14h), `disparo-newsletter.py` (sex 18h), `disparo-clustering.py` (03h)
- `scoring/inatividade_job.py` (06h)
- `meta-ads/orchestrator.py daily` (14h)

**Lançamento Cadência — entries cron mas NÃO operacional** (Felipe confirmou 25/05):
- `disparo-soap.py` (datas 4-29/05, ato 1-3 × email 1-5) — não dispara
- `dispatch/wa-broadcast-worker.py` (intercalado) — não dispara
- Implicação: NÃO bloqueia migração `/root/pd-marketing/`

**Lara (CS, dentro dos containers):**
- `lara-ceilandia daily_summary` (23h)
- `lara-central daily_summary` (23h), `ecuro_sync all` (09h), `funnel_report daily` (23h05), `funnel_report weekly` (sex 23h15)

**Cadência Growth (paths `/cadencia/` — pendente PDL-213 mover pra `/opt/cadencia-growth/`):**
- `crons/growth_pipeline.py sync ...` (14h), `newsletter` (sex 18h), `retry_provisioning.py` (13h55)
- `@reboot pipeline/trigger_server.py`, `mission_control.py`

### Crontab MASTER — 1 entry

```
*/5 * * * * sudo /opt/scripts/monitor-vps.sh
```

### UFW + Cloudflare

UFW configurado pra aceitar tráfego de Cloudflare (subnet `172.16.0.0/12` + `10.0.0.0/8` pra container interno). Porta 9300 exposta internamente pra Traefik rotear `alertas.cadencia.ia.br`.

---

## VPS Dev — interativo SSH (2.24.117.172)

**Acesso:** `ssh -i ~/.ssh/hostinger_dev_felipe felipe@2.24.117.172`
**Skill:** `/vps-dev`
**Sistema:** Ubuntu 24.04 (kernel 6.8)
**Users:** `felipe` (Felipe SSH), `luiz` (Luiz SSH)

### Característica fundamental

**Sem cron, sem systemd customizado.** Ambiente puro pra sessões SSH interativas com Claude Code (Felipe + Luiz). Toda automação determinística vive na Master.

### /home/felipe/

3 repos clonados:
- `Rotina/` — clone Rotina
- `cadencia-app/` — clone (Felipe review)
- `pd-portal/` — clone

CLIs: claude (Code), codex, gemini, node v24.15 (nvm), python 3.12.3.

### /home/luiz/

5 repos clonados:
- `cadencia-app/` (Luiz dev ativo)
- `pd-portal/` (Luiz dev ativo)
- `claude-dev-skills/` (skills Luiz)
- `ecuro-mcp/` (integração Ecuro GCI)
- `gci-go-whatsapp/` (WhatsApp GCI)

### /opt/

Vazio (só containerd do Docker engine).

---

## Bloqueios externos consolidados

| Bloqueio | Impacto |
|---|---|
| `/root/pd-marketing/` → `/opt/apps/pd-marketing/` | Workers Marketing precisam path estável antes de virar `times/marketing/workers/` |
| `/cadencia/` → `/opt/cadencia-growth/` (PDL-213) | Sub-squad Cadência Growth depende |
| PDL-215 (env vars Coolify 6 apps) | Squad Produto + Framework Luiz |

---

## Refresh quando

- Mudança grande de infra (nova VPS, reconfiguração, novo serviço systemd)
- Adição/remoção de containers
- Migração `/root/` → `/opt/apps/` for executada
- Mensalmente como check de drift
