---
date: 2026-05-22
tags: [infra, vps, docker, servicos, cron]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[marketing]]"]
---
# VPS Master — Serviços, Containers e Crons

---

## Containers Docker em execução

### Coolify (painel de deploy)

| Container | Imagem | Porta | Propósito |
|---|---|---|---|
| `coolify-proxy` | traefik:v3.3.5 | 80, 443, 8080 | Reverse proxy — roteia tráfego para containers gerenciados |
| `coolify` | coollabsio/coolify:4.1.0 | 8000 (interno) | Painel web de deploy |
| `coolify-db` | postgres:15-alpine | 5432 (interno) | Banco do Coolify |
| `coolify-redis` | redis:7-alpine | 6379 (interno) | Cache do Coolify |
| `coolify-realtime` | coollabsio/coolify-realtime:1.0.15 | 6001-6002 | WebSocket do painel |
| `coolify-sentinel` | coollabsio/sentinel:0.0.21 | — | Monitoramento interno do Coolify |

> Traefik fixado em v3.3.5 — **nunca atualizar sem checar changelog por "memory leak" ou "CPU spike"**. O auto-update está desativado no Coolify.

### Lara AI — cliente Sorria ⚠️ INTOCÁVEL

| Container | Imagem | Propósito |
|---|---|---|
| `lara-central` | openclaw-openclaw | Atendente IA — clínica Central Sorria |
| `lara-ceilandia` | openclaw-openclaw | Atendente IA — clínica Ceilândia Sorria |

Ambos construídos da imagem `openclaw-openclaw` (código em `/opt/openclaw/repo/` → repo `Posicionamento-Digital/lara-ai`). Sem portas expostas — recebem webhooks internamente.

**Não reiniciar, não recriar, não modificar sem avisar o cliente Sorria.**

### Cadência n8n ⚠️ INTOCÁVEL

| Container | Imagem | Porta | Propósito |
|---|---|---|---|
| `cadencia-n8n-main` | n8nio/n8n:2.19.5 | 5678 (localhost) | Orquestrador de workflows Cadência |
| `cadencia-n8n-worker-1` | n8nio/n8n:2.19.5 | 5678 (interno) | Worker de execução |
| `cadencia-n8n-runner-worker-1` | n8nio/runners:2.19.5 | 5680 (interno) | Runner de nós |
| `cadencia-postgres` | postgres:16-alpine | 5432 (interno) | Banco do n8n |
| `cadencia-redis` | redis (custom) | 6379 (interno) | Queue do n8n |
| `cadencia-redis-db` | redis:7-alpine | 6379 (interno) | Redis auxiliar |

**Nunca reiniciar, nunca modificar.** Afeta workflows de clientes pagantes.

### Ecuro Middleware

| Container | Imagem | Porta | Propósito |
|---|---|---|---|
| `ecuromiddleware-middleware-1` | ecuromiddleware-middleware | 8881→8080 | API middleware para sistema ecuro |
| `ecuromiddleware-ecuro-postgres-1` | postgres:16-alpine | 5432 (interno) | Banco do ecuro middleware |
| `ecuromiddleware-postgres-1` | postgres:16-alpine | 5432 (interno) | Banco auxiliar |

> Criado e mantido pelo Luiz. Não modificar sem consultá-lo. Composes em `/opt/lara-ai/ECURO Middleware/`.

---

## Docker daemon.json

Arquivo: `/etc/docker/daemon.json`

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "default-address-pools": [{"base":"10.0.0.0/8","size":24}],
  "live-restore": true,
  "default-ulimits": {
    "nofile": { "Name": "nofile", "Hard": 65000, "Soft": 65000 }
  }
}
```

> ⚠️ O Coolify pode sobrescrever este arquivo ao atualizar. Após qualquer atualização do Coolify, verificar se `live-restore` e `default-ulimits` ainda estão presentes.

---

## Portas abertas e o que roda em cada uma

| Porta | Protocolo | Processo | Exposto | Quem acessa |
|---|---|---|---|---|
| 22 | TCP | sshd | Sim | SSH — user master com chave |
| 80 | TCP | docker/Traefik | Sim | Só IPs Cloudflare (UFW) |
| 443 | TCP+UDP | docker/Traefik | Sim | Só IPs Cloudflare (UFW) |
| 8080 | TCP | docker/Traefik | Sim | Dashboard Traefik (sem auth — só interno) |
| 8765 | TCP | python3 | Sim | trigger_server.py — Cadência Growth |
| 8766 | TCP | python3 | Sim | cadencia-webhook.service |
| 8768 | TCP | python3 | Sim | Serviço Python (identificar) |
| 8881 | TCP | docker/ecuro | Sim | Ecuro Middleware API |
| 9090 | TCP | systemd | Sim | Cockpit (bloqueado no UFW? verificar) |
| 19999 | TCP | netdata | Não | Bloqueado via UFW — só SSH tunnel |
| 39090 | TCP | python3 | Sim | (identificar — estava pré-existente) |
| 20241 | TCP | cloudflared | Localhost | Cloudflare Tunnel (só localhost) |
| 5678 | TCP | docker/n8n | Localhost | n8n UI (só localhost) |
| 4317/4318 | TCP | alloy | Todos | OTLP receiver para traces/metrics |

---

## Serviços systemd

### cadencia-webhook.service

```
Descrição: Cadencia Growth Scoring Webhook Handler
User: master
WorkingDirectory: /cadencia
EnvironmentFile: /cadencia/.env
ExecStart: /usr/bin/python3 /cadencia/scoring/webhook_handler.py
Restart: always
```

Recebe webhooks de scoring do sistema Cadência. Porta 8766.

```bash
# Status
sudo systemctl status cadencia-webhook.service

# Logs
sudo journalctl -u cadencia-webhook.service -f
```

### stamper-bot.service

```
Descrição: Stamper Telegram Bot (Claude-powered)
User: master
WorkingDirectory: /opt/stamper-telegram-bot
ExecStart: /opt/stamper-telegram-bot/venv/bin/python3 bot.py
Restart: always
```

Bot Telegram de gestão interna da PD.

```bash
sudo systemctl status stamper-bot.service
sudo journalctl -u stamper-bot.service -f
```

### alloy.service

Grafana Alloy — coleta métricas e envia para Grafana Cloud.

- Config: `/etc/alloy/config.alloy`
- Destino: Grafana Cloud stack 1632821 (conta do Luiz — verificar credenciais)
- Coleta: métricas GCI GO WhatsApp via OTLP (portas 4317/4318)

---

## Crons — root (crontab do root)

> Estes crons serão migrados para dentro dos containers quando a containerização for concluída.

### pd-marketing (em `/root/pd-marketing/`)

| Horário | Script | O que faz |
|---|---|---|
| 05:00 diário | disparo-ideacao.py | Gera ideias de conteúdo |
| 00:00 diário | disparo-blog.py | Dispara blog (madrugada) |
| 14:00 diário | disparo-blog.py | Dispara blog (tarde) |
| 14:00 diário | disparo-seinfeld.py | Dispara email Seinfeld |
| 18:00 sexta | disparo-newsletter.py | Dispara newsletter |
| 06:00 diário | scoring/inatividade_job.py | Scoring de inatividade |
| 03:00 diário | disparo-clustering.py | Clustering de leads |
| 14:00 diário | meta-ads/orchestrator.py | Meta Ads diário |

> **⚠️ Status atual:** scripts quebrados — API key GHL inválida (ver PDL-156). SOAP ATO 3 em andamento até 29/05.

### Lara / Sorria (via docker exec)

| Horário | Comando | O que faz |
|---|---|---|
| 23:00 diário | `docker exec lara-ceilandia python3 -m src.clients.sorria.ceilandia.daily_summary` | Resumo diário Ceilândia |
| 23:00 diário | `docker exec lara-central python3 -m src.clients.sorria.central.daily_summary` | Resumo diário Central |
| 09:00 diário | `docker exec lara-central python3 -m src.clients.sorria.ecuro_sync all` | Sync eCuro |
| 23:05 diário | `docker exec lara-central python3 -m src.clients.sorria.funnel_report daily` | Relatório funil diário |
| 23:15 sexta | `docker exec lara-central python3 -m src.clients.sorria.funnel_report weekly` | Relatório funil semanal |

### Cadência Growth (em `/cadencia/`)

| Horário | Script | O que faz |
|---|---|---|
| 14:00 diário | growth_pipeline.py sync blog seinfeld linkedin instagram | Pipeline de conteúdo completo |
| 13:55 diário | retry_provisioning.py | Retenta provisioning com falha |
| 18:00 sexta | growth_pipeline.py newsletter | Newsletter dos tenants |
| @reboot | trigger_server.py | Servidor webhook (porta 8765) |
| @reboot | mission_control.py | Gerenciador de pipelines |

---

## Crons — master (crontab do master)

| Horário | Script | O que faz |
|---|---|---|
| A cada 5 min | `sudo /opt/scripts/monitor-vps.sh` | Verifica load, CLOSE_WAIT, RAM Traefik, envia WhatsApp se alert |

Log: `/var/log/monitor-vps.log`

---

## Comandos úteis de operação

```bash
# Ver todos os containers
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Logs de um container
docker logs <nome> --tail 100 -f

# Reiniciar um container (com cuidado)
docker restart <nome>

# Ver consumo de recursos
docker stats --no-stream

# Ver logs do sistema
sudo journalctl -f

# Verificar crons do root
sudo crontab -l

# Verificar crons do master
crontab -l

# Status dos serviços systemd
systemctl list-units --type=service --state=running
```

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Projetos-opt]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Monitoramento]]
