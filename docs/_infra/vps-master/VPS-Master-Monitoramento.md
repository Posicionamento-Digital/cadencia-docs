---
date: 2026-05-22
tags: [infra, vps, monitoramento, netdata, grafana, alertas]
moc: "[[MOC-Infra]]"
type: source
entities: ["[[Cadencia]]", "[[ecuro-mcp]]"]
---
# VPS Master — Monitoramento e Observabilidade

---

## Camadas de monitoramento

| Ferramenta | O que monitora | Como acessar |
|---|---|---|
| **Netdata** | Métricas em tempo real (CPU, RAM, containers, rede) | SSH tunnel → localhost:19999 |
| **Cockpit** | Gerenciamento do servidor (processos, disco, logs, terminal) | SSH tunnel → localhost:9090 |
| **Grafana Cloud** | Métricas históricas + traces (Alloy coletando desde 11/05) | Conta Luiz — login pendente |
| **Script monitor-vps.sh** | Alertas proativos (load, CLOSE_WAIT, RAM Traefik) | WhatsApp automático |

---

## Netdata

**Porta:** 19999 (bloqueada no UFW — só via SSH tunnel)

**Como acessar:**
```bash
ssh -L 19999:localhost:19999 vps-master
# Abrir: http://localhost:19999
```

**O que mostra:**
- CPU, RAM, disco em tempo real
- Consumo por container Docker individualmente
- Conexões de rede, sockets TCP
- Load average e processos

**Alertas nativos:** Netdata pode enviar alertas por email ou webhook. Não configurado ainda.

---

## Cockpit

**Porta:** 9090 (via systemd socket)

**Como acessar:**
```bash
ssh -L 9090:localhost:9090 vps-master
# Abrir: http://localhost:9090
# Login: usuário master (credenciais do sistema)
```

**O que permite:**
- Ver e gerenciar serviços systemd (start/stop/restart)
- Terminal web (alternativa ao SSH puro)
- Ver logs do sistema
- Atualizar pacotes
- Monitorar disco e RAM

---

## Grafana Cloud (Alloy)

**Status:** coletando desde 11/05/2026 — dados históricos já existem.

**Stack ID:** 1632821

**O Alloy coleta:**
- Métricas via Prometheus remote write → `prometheus-prod-40...grafana.net`
- Logs via Loki → `logs-prod-024.grafana.net`
- Traces via OTLP (portas 4317/4318) — GCI GO WhatsApp envia traces

**Config do Alloy:** `/etc/alloy/config.alloy`

**API key:** configurada via environment variable no systemd (`/etc/systemd/system/alloy.service.d/env.conf`) — não exposta neste documento.

**Login Grafana Cloud:** conta criada pelo Luiz (email pendente de confirmação). Acessar: `https://grafana.com`

**Para conectar mais projetos ao OTLP receiver:**
Qualquer serviço pode enviar traces/metrics para `http://host.docker.internal:4318` (HTTP) ou `host.docker.internal:4317` (gRPC). O Alloy repassa automaticamente para o Grafana Cloud.

---

## Script monitor-vps.sh

**Localização:** `/opt/scripts/monitor-vps.sh`

**Cron master:** `*/5 * * * * sudo /opt/scripts/monitor-vps.sh`

**Log:** `/var/log/monitor-vps.log`

**O que verifica a cada 5 minutos:**

| Métrica | Threshold | Indica |
|---|---|---|
| Load average | > número de CPUs | Servidor sobrecarregado |
| Conexões CLOSE_WAIT | > 1.000 | Possível SYN flood |
| Sockets TCP no kernel | > 10.000 | Volume anormal de conexões |
| RAM do Traefik (coolify-proxy) | > 500MiB | Memory leak ou flood |

**Quando alerta:** envia WhatsApp para o número do Felipe via API Stevo.

**Verificar log:**
```bash
tail -20 /var/log/monitor-vps.log

# Formato de cada linha:
# 2026-05-22 21:45 | load:0/1 | close_wait:3 | sockets:385 | traefik:22MiB
```

**Rodar manualmente:**
```bash
sudo /opt/scripts/monitor-vps.sh
```

---

## Diagnóstico rápido durante incidente

```bash
# Resumo geral do servidor
htop

# Estado das conexões TCP
ss -s

# Conexões CLOSE_WAIT (flood indicator)
ss -nt state close-wait | wc -l

# Consumo de recursos por container
docker stats --no-stream

# RAM específica do Traefik
docker stats coolify-proxy --no-stream --format '{{.MemUsage}}'

# Sockets no kernel
sudo cat /proc/net/sockstat

# Logs do Traefik
docker logs coolify-proxy --tail 100 -f

# Logs gerais do sistema
sudo journalctl -f --since "5 minutes ago"
```

---

## Sentry (monitoramento de erros de código)

**Status:** cloud gratuito (5k erros/mês, 10k transações/mês).

**Hoje monitorado:** Cadência (Next.js frontend).

**Projetos a conectar no futuro:**
- cadencia-workers (Railway)
- gci-go-whatsapp
- ecuro-mcp

**Como conectar um projeto:** adicionar SDK Sentry no código + configurar `SENTRY_DSN` como variável de ambiente.

---

## Notas Relacionadas

[[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Arquitetura]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Seguranca]] · [[Infra/VPS-Hostinger/VPS-Master/VPS-Master-Servicos]]
