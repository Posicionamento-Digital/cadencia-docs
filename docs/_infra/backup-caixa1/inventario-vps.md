---
data: 2026-08-08
issue: DEV-1727
projeto: Infra — Backup + Cloud CAIXA1
---

# Inventário VPS Dev + VPS Master — 2026-08

Snapshot do que roda em cada VPS pra basear os scripts de backup da F4 (DEV-1731). Coletado via SSH em 2026-08-08.

## VPS Dev (2.24.117.172)

**Disco:** `/dev/sda1` 96 GB, 38 GB usado (39%).

### Containers Docker

| Container | Imagem | Papel |
|---|---|---|
| `cadencia-agenda-app` | `easyappointments:latest` | EasyAppointments (agenda) |
| `cadencia-agenda-mysql` | `mysql:8.0` | DB EasyAppointments |
| `lara-api` | `lara-lara-api` | **Lara nova (Cadencia)** — API |
| `lara-worker` | `lara-lara-worker` | Lara nova — worker |
| `lara-redis` | `redis:7-alpine` | Lara nova — cache |
| `lara-postgres` | `pgvector/pgvector:pg16` | Lara nova — DB (vetorial) |

### Volumes nomeados relevantes
- `lara-postgres-data` — **DB da Lara nova (Cadencia)**
- `lara-redis-data`
- `cadencia-agenda-mysql-data`

### Crons (user `felipe`)
- `0 23 * * *` — sync dev-docs
- `*/10 * * * *` — health-dev selfreport
- `5 8-22 * * *` — pos-briefing trigger

### Crons (root)
- `0 11 * * 1-5` — daily-brief morning
- `30 21 * * 1-5` — daily-brief evening

### Systemd services notáveis
`cloudflared`, `pd-syslog`, `monarx-agent`, `docker`, `ssh`.

---

## VPS Master (72.60.4.71)

**Disco:** `/dev/sda1` 96 GB, 34 GB usado (35%).

### Coolify stack (core)

| Container | Imagem | Papel |
|---|---|---|
| `coolify` | `coollabsio/coolify:4.1.2` | UI + orchestrator |
| `coolify-db` | `postgres:15-alpine` | Banco interno Coolify (metadata: apps, envs, servers) |
| `coolify-redis` | `redis:7-alpine` | Cache Coolify |
| `coolify-realtime` | `coolify-realtime:1.0.16` | WebSockets UI |
| `coolify-sentinel` | `sentinel:0.0.21` | Metrics |
| `coolify-proxy` | `traefik:v3.3.5` | Reverse proxy 80/443/8080 |
| `nset1suf...-helper` | `coolify-helper:1.0.14` | Deploy helper |

### Apps deployados via Coolify (identificados)

| Serviço | Container/Volume-chave | Observação |
|---|---|---|
| **Evolution API (WhatsApp Evo)** | `evolution-otklj*` + `postgres-otklj*` + `otklj844u...-lara-evolution-db-data` | Instância principal WhatsApp |
| **Lara legada (GCI)** | `u5n5f0zt...-lara-postgres-data`, `-lara-redis-data` | **NÃO é a Lara nova — é a legada do grupo GCI** |
| **Ecuro middleware** | `ecuromiddleware_postgres_data`, `yoe8tkelor...-ecuro-middleware-postgres-data` | Integração cliente GCI-GO |
| **Confirmation-queue (Temporal)** | `kc93gui9...-confirmation-queue-postgres/redis/temporal-postgres-data` | Sistema fila confirmação agenda |
| **EasyAppointments (Master)** | `cadencia-agenda-db-data`, `cadencia-agenda-storage` | Cópia/versão prod da agenda |
| **Obsidian web (?)** | `obsidian_caddy_data`, `obsidian_caddy_config` | Caddy servindo algum vault via web |
| **Portainer** | `portainer_data` | UI Docker adicional |
| **Redis genérico** | `redis-data-j12rhf42*` | Container `j12rhf42*` (identificar app depois) |

### Crons (user `master`)
- `*/5 * * * *` — monitor-vps
- `0 6 * * *` — state-aggregator (pd-framework)
- `30 21 * * *` — health-check digest + notify
- `0 * * * *` — health-check apply
- `*/30 * * * *` — health-check deadman
- `50 21 * * *` — digest heartbeat
- `15 21 * * *` — conferencia-cobranca-pasta worker
- `*/10 * * * *` — deploy_watcher (Supabase + Slack)
- `30 7 * * *` — self_test_suite (framework)
- `0 8 * * *` — hostinger_watcher (billing/estado VM)
- `0 9 * * *` — confirmacao-agenda worker

### Crons (root — cadencia)
- `0 18 * * 5` — growth_pipeline newsletter (sexta 18h)
- `0 14 * * *` — growth_pipeline sync blog seinfeld instagram
- `55 13 * * *` — retry_provisioning
- `@reboot` — mission_control
- `* * * * *` — collect-custom-metrics
- `*/5 * * * *` — cleanup_orphan_ideas
- `0 12 * * *` — drift_check
- `@reboot` — resend_webhook
- `*/5 * * * *` — cadence_tick
- `0 12 * * *` — supabase-advisors
- `0 12 * * *` — check_onboarding_stalled
- `0 12 * * 1` — audit_resend_domains (segunda)
- `*/5 * * * *` — evo-pg-guard
- `0 16 * * *` — blog_healthcheck
- `0 * * * *` — reap_stuck_jobs

⚠️ **Segurança pendente (não bloqueia backup):** `VERCEL_TOKEN` em texto claro no início do crontab root — Felipe ciente, rotação em separado.

### Systemd services notáveis
`cadencia-trigger`, `grafana-webhook`, `onboarding-consumer` (fila webhook→consolidador), `alloy` (OpenTelemetry), `cloudflared`, `docker`, `ssh`.

---

## Estratégia de backup por fonte (base pra F4)

| Fonte | Tipo | Estratégia |
|---|---|---|
| VPS Dev `/home/felipe`, `/home/luiz`, `/opt` | filesystem | restic via SSH |
| VPS Dev — DB Lara nova (`lara-postgres`) | container Postgres | `docker exec lara-postgres pg_dump ...` → arquivo → restic |
| VPS Dev — MySQL EasyAppointments | container MySQL | `docker exec cadencia-agenda-mysql mysqldump ...` → arquivo → restic |
| VPS Dev — Redis Lara | container Redis | `docker exec lara-redis redis-cli SAVE` + copiar RDB (dado é cache — vale se dá pra reconstruir?) |
| VPS Dev — crontabs | export | `crontab -l` + `sudo crontab -l` → arquivo → restic |
| VPS Master `/opt`, `/etc`, `/root/scripts` | filesystem | restic via SSH |
| VPS Master — Coolify metadata | banco interno | **Backup nativo Coolify** (dashboard → destination S3-compat na CAIXA1 ou dump manual do `coolify-db`) |
| VPS Master — DBs dos apps gerenciados (Evolution, Lara legada, Ecuro, Confirmation-queue, EasyAppointments) | container Postgres/MySQL | `docker exec <db> pg_dump/mysqldump` por container identificado |
| VPS Master — Docker volumes não-DB (storage, config) | volumes | restic `/var/lib/docker/volumes/` (arquivos raw — funciona pra config/storage, não pra DB "quente") |
| VPS Master — crontabs (user + root) | export | idem VPS Dev |

## Perguntas em aberto (não bloqueiam F0)
1. `redis-data-j12rhf42*` → qual app dono? (identificar em F4 quando escrever script)
2. `obsidian_caddy_data` → algum vault Obsidian exposto via Caddy web? Vale backup?
3. Confirmation-queue Temporal → Temporal tem workflows em execução — precisa graceful drain antes de dump?

## Referências
- Issue: [DEV-1727](https://linear.app/cadencia/issue/DEV-1727)
- Issue-mãe: [DEV-1726](https://linear.app/cadencia/issue/DEV-1726)
- Coleta bruta: `ssh vps-dev` + `ssh -i ~/.ssh/hostinger_prod_master master@72.60.4.71` em 2026-08-08 22:20
