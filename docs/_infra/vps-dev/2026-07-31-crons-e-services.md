# Crons + systemd customizados — VPS Dev

> Fonte: `crontab -l` (user root e felipe), `ls /etc/systemd/system/*.service`, `systemctl status` de cada.

## Systemd customizados (2 units da PD + cloudflared)

### `cloudflared.service` ✅ ATIVO — CRÍTICO

Tunnel Cloudflare que expõe endpoints internos. Documento dedicado: [`cloudflared-tunnel.md`](cloudflared-tunnel.md).

```
Loaded: /etc/systemd/system/cloudflared.service (enabled, preset: enabled)
Active: since 2026-07-30 20:22:54 UTC (subiu no reboot pós-desligamento)
Main PID: 775 (cloudflared)
Memory: 53.7M
ExecStart: /usr/bin/cloudflared --no-autoupdate tunnel run --token <TOKEN>
```

**Se cair:** Lara GCI-GO fica offline pros 3 tenants Sorria Goiás (`lara.cadencia.ia.br` deixa de responder).

### `pd-syslog.service` ⚠️ VAI ERRAR

```
Loaded: /etc/systemd/system/pd-syslog.service (active)
ExecStart: /usr/local/sbin/pd-syslog --users luiz
User: root
Restart: always (RestartSec=60)
```

Serviço custom que faz "system telemetry sync" (a descrição no unit file — não achei código-fonte de `pd-syslog` no framework). Roda como root, envia telemetria dos processos/logs do user `luiz` pra algum destino remoto.

**Problema desde 30/07:** user `luiz` está inerte (sem processos, sem sessões). O serviço vai gerar telemetria vazia ou erro toda vez que executa. Não vai crashar (Restart=always + RestartSec=60 mantém up), mas polui logs.

**Ação recomendada:** ou (a) desligar `sudo systemctl disable --now pd-syslog`; ou (b) reescrever pra `--users felipe` (se o objetivo era monitorar atividade dev). Precisa entender o que era esse `pd-syslog` originalmente — checar `_core/` no framework, pode ser da DEV-866 (Sync estado dev do Luiz).

### Outros systemd (não-PD, não mexer)

```
cloudflared-update.service     # auto-update do cloudflared (default do install)
dbus-org.freedesktop.*         # DBus infra padrão Ubuntu
iscsi.service                  # iSCSI (não usado ativamente aqui)
syslog.service                 # syslog padrão
vmtoolsd.service               # VMware/QEMU tools da VPS
```

## Cron user root (2 entries)

Vive em `/var/spool/cron/crontabs/root` (`sudo crontab -u root -l`).

### `daily-brief` — Stamper Gestão async

```cron
0 11 * * 1-5  HOME=/root /usr/bin/python3 /opt/daily-brief/brief.py --target morning \
              >> /var/log/daily-brief/morning.log 2>&1

30 21 * * 1-5 HOME=/root /usr/bin/python3 /opt/daily-brief/brief.py --target evening \
              >> /var/log/daily-brief/evening.log 2>&1
```

Roda dias úteis 11h (morning brief) e 21h30 (evening brief).

**Código:** `/opt/daily-brief/brief.py` + `queue.py` (versões `.bak` de 2026-06-24 e 2026-06-09 preservadas — histórico).

**Contexto:** Stamper Gestão Async Fase 3a — gera briefing diário do Felipe. Provavelmente escreve em Obsidian ou envia notificação Stevo/Evo. Precisa ler código pra confirmar destino (out of scope deste doc).

### `luiz-state` snapshot ⚠️ ÓRFÃO

```cron
40 21 * * 1-5 HOME=/root /opt/luiz-state/luiz_state_cron.sh \
              >> /var/log/luiz-state.log 2>&1
```

Roda dias úteis 21h40 — snapshot do estado dev do Luiz (DEV-866).

**Código:** `/opt/luiz-state/luiz_state.py` + `luiz_state_cron.sh`.

**Problema desde 30/07:** user luiz inerte + home deletado no primeiro dia de desligamento (depois recriado inerte). Script vai falhar ou gerar snapshot vazio.

**Ação:** desligar (`crontab -u root -e` remove essa linha) OU deletar os arquivos em `/opt/luiz-state/`.

## Cron user felipe (7 entries)

Vive em `/var/spool/cron/crontabs/felipe`. **NÃO precisa sudo pra editar** (é do próprio user).

### `sync-dev-docs` — sync noturno

```cron
0 23 * * *  /usr/bin/python3 /opt/sync-dev-docs.py >> /opt/dev-docs/.sync.log 2>&1
```

Script `/opt/sync-dev-docs.py` (script root, executável, 2595 bytes) — sync de docs `/opt/dev-docs/`. Roda 23h todo dia. Precisa ler código pra confirmar o que sincroniza (não é `/documentar-software` — é outra coisa).

### `cadencia-autofix` — CAD-689 loop autofix

```cron
*/15 * * * * flock -n /tmp/autofix.lock /home/felipe/cadencia-autofix/run.sh \
             >> /home/felipe/cadencia-autofix/run.log 2>&1
```

A cada 15min. `flock=-n` garante 1 instância só. Pega issues `own:agente` in-progress e tenta rodar agente autofix. Detalhe:
- `/home/felipe/cadencia-autofix/README.md` (não lido)
- `autofix_worker.py` + `run.sh` + `run.log`
- Log de exemplo: `voo-dev944.log` (DEV-944 = alguma issue trabalhada)

### `health-dev` — self-report

```cron
*/10 * * * * /usr/bin/python3 /home/felipe/health-dev/dev_selfreport.py \
             >> /home/felipe/health-dev/run.log 2>&1
```

A cada 10min. Provavelmente reporta health desta VPS Dev pra algum dashboard/hub (Grafana? Sentry? Linear?). Precisa ler código pra saber destino.

### `pos-briefing` — CSE-97 trigger transcrição Fireflies

```cron
5 8-22 * * * flock -n /tmp/pos-briefing.lock /home/felipe/pos-briefing-trigger.sh \
             >> /home/felipe/pos-briefing-trigger.log 2>&1
```

5 minutos após cada hora, das 8h às 22h. Script (lido):
```bash
# Detecta transcrição nova (Fireflies) e dispara a cadeia pós-briefing (dry-run;
# apply é gate do Felipe). Padrão do autofix run.sh.
export HOME=/home/felipe
export OP_SERVICE_ACCOUNT_TOKEN=$(cat /home/felipe/.config/op/service-account-token)
export POS_BRIEFING_INBOX=/home/felipe/transcricoes-inbox
export INTERACAO_ORIGEM=automatico
cd /home/felipe/pd-framework-main/times/cs/workers/pos-briefing-trigger || exit 0
[ -f worker.py ] || exit 0
exec python3 worker.py --once
```

⚠️ **Path desatualizado:** aponta pra `/home/felipe/pd-framework-main/` — o clone canônico é `/home/felipe/pd-framework/` (sem `-main`). Se `pd-framework-main` não existir, script sai silenciosamente (`|| exit 0`). Precisa confirmar qual clone está sendo usado ou ajustar path.

### `motor-notify` — notifica Felipe sobre eventos do Motor

```cron
*/10 * * * * flock -n /tmp/motor-notify.lock \
             /home/felipe/pd-framework/_core/motor_notify_cron.sh \
             >> /home/felipe/pd-framework/.pd/motor-notify.log 2>&1
```

A cada 10min. Detecta PRs abertos pelo Motor, blocked, done — notifica Felipe no WhatsApp. Detalhe em [`stack-pd-motor.md`](stack-pd-motor.md).

### `stale-claim-reaper` — DEV-1344 libera claims órfãos

```cron
7 * * * * flock -n /tmp/stale-reaper.lock \
          /home/felipe/pd-framework/_core/stale_claim_reaper_cron.sh \
          >> /home/felipe/pd-framework/.pd/stale-reaper.log 2>&1
```

7min de cada hora. Libera claims `own:agente` que ficaram órfãos (worker morreu no meio). 2 estágios, cap 5/run.

## Resumo por health (o que precisa ação)

| Item | Health | Ação |
|---|---|---|
| `cloudflared.service` | ✅ OK | monitorar |
| `pd-syslog.service` | ⚠️ vai errar | disable OU reescrever pra `--users felipe` |
| Cron root `daily-brief` | ✅ OK | monitorar logs |
| Cron root `luiz-state` | ⚠️ órfão | remover linha do crontab |
| Cron felipe `sync-dev-docs` | ❓ não validado | ler `/opt/sync-dev-docs.py` |
| Cron felipe `cadencia-autofix` | ✅ ativo (CAD-689) | monitorar |
| Cron felipe `health-dev` | ❓ não validado | ler `dev_selfreport.py` |
| Cron felipe `pos-briefing` | ⚠️ path errado (`pd-framework-main`) | ajustar path ou criar symlink |
| Cron felipe `motor-notify` | ✅ ativo | monitorar |
| Cron felipe `stale-reaper` | ✅ ativo | monitorar |

## Refs

- Systemd units: `/etc/systemd/system/`
- Crontabs: `/var/spool/cron/crontabs/{root,felipe}`
- Logs cron: `/var/log/daily-brief/`, `/var/log/luiz-state.log`, `/home/felipe/**/run.log`, `.pd/*.log`
- DEV-866 (luiz-state sync): mencionado no comentário do cron
- CSE-97 (pos-briefing): mencionado no comentário do cron
- CAD-689 (autofix loop): mencionado no comentário do cron
- DEV-1344 (stale reaper): mencionado no comentário do cron
