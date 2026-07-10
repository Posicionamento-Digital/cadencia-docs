---
date: 2026-05-24
tags: [infra, monitoramento, grafana, vps, alertas]
moc: "[[Infra/VPS Master]]"
type: source
entities: ["[[Cadencia]]"]
---
# Stack de Monitoramento — VPS Master

Documentação técnica completa da stack de observabilidade e alertas da VPS Master (`72.60.4.71`), construída em 2026-05-24.

---

## Visão Geral

```
VPS Master
  └── Grafana Alloy (agente)
        ├── Coleta métricas do sistema (CPU, RAM, disco, rede, load)
        ├── Lê métricas customizadas do textfile_collector (Traefik RAM, CLOSE_WAIT, Vercel)
        └── Faz scraping de logs (auth.log, ufw.log)
              │
              ▼
        Grafana Cloud (felipeluissalgueiro.grafana.net)
              ├── Prometheus (métricas)  ──► Alert Rules
              └── Loki (logs)            ──► Alert Rules
                                               │
                                               ▼
                                    Contact Point: Webhook
                                    https://alertas.cadencia.ia.br/webhook
                                               │
                              ┌────────────────┴────────────────┐
                              ▼                                 ▼
                     WhatsApp (Stevo)                  Linear (issue automática)
                   +55 11 91491-2127                   team: Posicionamento Digital
```

---

## Componentes

### 1. Grafana Alloy — Agente de Coleta

**Localização:** VPS Master, instalado pelo Fleet Management do Grafana Cloud  
**Config:** `/etc/alloy/config.alloy`  
**Serviço:** `systemctl status alloy`

O Alloy é o agente que roda na VPS e envia dados para o Grafana Cloud. Ele:
- Coleta métricas do sistema via `prometheus.exporter.unix` (CPU, RAM, disco, rede, load average, conexões)
- Lê métricas customizadas do diretório `/var/lib/node_exporter/textfile_collector/` (textfile_collector)
- Faz scraping dos logs de segurança e os envia para o Loki

Trecho relevante do config:

```hcl
prometheus.exporter.unix "local" {
  textfile {
    directory = "/var/lib/node_exporter/textfile_collector"
  }
}

loki.source.file "security_logs" {
  targets = [
    {__path__ = "/var/log/auth.log", job = "auth", host = "vps-master"},
    {__path__ = "/var/log/ufw.log",  job = "ufw",  host = "vps-master"},
  ]
  forward_to = [loki.write.grafana_cloud_loki.receiver]
}
```

**Labels que chegam no Grafana:**
- `job = "integrations/unix"` (sobrescrito pelo Fleet Management — não é "vps-master")
- `instance = "main"`

---

### 2. Coletor de Métricas Customizadas

**Script:** `/opt/scripts/collect-custom-metrics.py`  
**Execução:** cron root, a cada 1 minuto (`* * * * *`)  
**Saída:** `/var/lib/node_exporter/textfile_collector/custom_metrics.prom`

Coleta métricas que o Alloy não captura nativamente:

| Métrica | Fonte | O que mede |
|---|---|---|
| `traefik_memory_bytes` | `docker stats coolify-proxy` | RAM do container Traefik em bytes |
| `tcp_close_wait_total` | `ss -ant` | Conexões TCP presas em CLOSE_WAIT |
| `vercel_deploy_failed{project="..."}` | Vercel API v9 | 1 se último deploy falhou, 0 se ok |

**Detalhes técnicos:**
- Escrita atômica via `tempfile.mkstemp` + `os.rename` — evita leitura de arquivo parcial
- `os.chmod(tmp, 0o644)` antes do rename — obrigatório para o usuário `alloy` conseguir ler (o cron roda como root, o Alloy como `alloy`)
- Token Vercel carregado via `VERCEL_TOKEN` no crontab root
- 16 projetos Vercel monitorados (todos os que existem na conta)

**Para adicionar nova métrica:**
```python
lines.append("# HELP nome_da_metrica Descricao")
lines.append("# TYPE nome_da_metrica gauge")
lines.append(f"nome_da_metrica {valor}")
```

---

### 3. Alert Rules no Grafana

**Grupo:** `vps-infra` e `vps-security`  
**Folder UID:** `cfn2d5qqfy41sa`

Todas as regras usam o pipeline obrigatório do Grafana Unified Alerting:
```
A (PromQL query) → B (Reduce: last) → C (Math: condição)
```
Não é possível comparar time series diretamente no step Math — precisa do Reduce no meio.

| Issue | Rule UID | PromQL | Threshold | For |
|---|---|---|---|---|
| VPS Load Average Alto | `ffn2f1b3qgwsgf` | `node_load1` vs `count(node_cpu_seconds_total{mode="idle"})` | load > nCPUs | 5m |
| Traefik RAM Alta | `afn2f1bk1b20wd` | `traefik_memory_bytes` | > 524288000 (500MiB) | 5m |
| TCP CLOSE_WAIT Excessivo | `cfn2f1c04ni80c` | `tcp_close_wait_total` | > 1000 | 5m |
| Disco Raiz Baixo | `efn2f1cewjvuof` | `round(100 * avail / size)` mountpoint=/ | < 15% | 10m |
| RAM Disponível Baixa | `dfn2f1csrzkzkc` | `round(100 * MemAvailable / MemTotal)` | < 20% | 10m |
| SSH Brute Force | `efn2eexj5brb4c` | Loki: `count_over_time({job="auth"} \|= "Failed password" [5m])` | > 10 | 0s |
| Vercel Deploy Falhado | `cfn2guy3315a8e` | `max(vercel_deploy_failed)` | >= 1 | 2m |

**Criar nova alert rule via API:**
```python
SA = os.environ["GRAFANA_SA_TOKEN"]  # 1Password: Hosts > "Grafana - Service account token - ClaudeCode" (campo credencial). Carregar via `op item get` antes de rodar.

payload = {
    "title": "Nome da Regra",
    "ruleGroup": "vps-infra",
    "folderUID": "cfn2d5qqfy41sa",
    "condition": "C",
    "data": [
        query_step("A", 'sua_metrica{job="integrations/unix"}'),
        reduce_step("B", "A"),   # Reduce: last
        math_step("C", "$B > threshold"),
    ],
    "for": "5m",
    "labels": {"severity": "high"},
    "annotations": {"summary": "...", "description": "..."},
    "noDataState": "OK",
    "execErrState": "Error"
}

curl -X POST "https://felipeluissalgueiro.grafana.net/api/v1/provisioning/alert-rules" \
  -H "Authorization: Bearer $SA" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Scripts de referência: `C:\temp\create-alert-rules-v2.py`

---

### 4. Webhook de Alertas

**Código:** `/opt/grafana-webhook/main.py`  
**URL pública:** `https://alertas.cadencia.ia.br/webhook`  
**Porta interna:** `9300`  
**Serviço:** `grafana-webhook.service` (systemd, user `master`)  
**Secrets:** `/opt/grafana-webhook/.env`

#### Fluxo de um alerta

```
Grafana Cloud dispara alert
  │
  ▼ POST /webhook
  X-Webhook-Secret: <hash>
  ├── Valida secret
  ├── Parseia payload Alertmanager (campo "alerts") ou formato simples
  └── Para cada alert:
        ├── Detecta squad via labels.ruleGroup (vps-infra→infra, vps-security→security)
        ├── Envia WhatsApp via Stevo (sempre)
        └── Se status == "firing":
              ├── Calcula fingerprint (campo alert.fingerprint ou MD5 de alertname+labels)
              ├── Checa cache /opt/grafana-webhook/alert_cache.json (TTL 30min)
              ├── Se duplicata → skip Linear
              └── Se novo → cria issue Linear com título [ALERTA][squad] nome
```

#### Variáveis de ambiente (.env)

| Variável | Descrição |
|---|---|
| `WEBHOOK_SECRET` | Hash para autenticar chamadas do Grafana |
| `STEVO_API_URL` | `https://sm-canguru.stevo.chat` |
| `STEVO_API_KEY` | API key do Stevo (mesmo que o `/opt/scripts/monitor-vps.sh` lê) |
| `STEVO_PHONE` | `5511914912127` (Felipe) |
| `LINEAR_TOKEN` | `lin_api_*` — token Linear para criar issues |
| `LINEAR_TEAM_ID` | `3d9699c8-ee89-466d-804d-8237041080d1` (time PDL) |

Todos os valores estão no 1Password — consultar `mapa-1password.md`.

#### Roteamento Traefik

Arquivo: `/data/coolify/proxy/dynamic/grafana-webhook.yaml`

```yaml
http:
  routers:
    grafana-webhook-https:
      rule: Host(`alertas.cadencia.ia.br`)
      service: grafana-webhook
      tls:
        certresolver: letsencrypt
  services:
    grafana-webhook:
      loadBalancer:
        servers:
          - url: http://host.docker.internal:9300
```

O Traefik (container `coolify-proxy`) roteia `alertas.cadencia.ia.br` → `host.docker.internal:9300` → serviço na porta 9300 do host. O UFW permite acesso à 9300 pela subnet Docker (`172.16.0.0/12` e `10.0.0.0/8`).

---

### 5. monitor-vps.sh (complementar)

**Script:** `/opt/scripts/monitor-vps.sh`  
**Execução:** crontab do usuário `master`, a cada 5 minutos (`*/5 * * * *`)  
**Log:** `/var/log/monitor-vps.log`

Complementa o Grafana cobrindo **apenas o que o Grafana não monitora:**

| Métrica | Threshold | Ação |
|---|---|---|
| Sockets TCP totais (SOCKSTAT) | > 10.000 | WhatsApp via Stevo |

Load, CLOSE_WAIT e Traefik RAM **não alertam mais pelo script** — estão cobertos pelo Grafana com melhor roteamento (WhatsApp + Linear). O script ainda **loga** essas métricas localmente.

A key do Stevo não está hardcoded — é lida de `/opt/grafana-webhook/.env` via `source`.

---

## Credenciais — onde estão no 1Password

| O que | Vault | Item |
|---|---|---|
| Grafana SA token (Admin) | Hosts | `Grafana - Service account token - ClaudeCode` |
| Grafana Cloud API key | Hosts | `Grafana Cloud - API - VPS Master` |
| Stevo API key | Hosts (via .env) | lido de `/opt/grafana-webhook/.env` |
| Vercel token | Hosts | `Vercel - api - cli` |
| Linear token | Hosts (via .env) | lido de `/opt/grafana-webhook/.env` |

---

## O que NÃO está implementado (pendências)

| Item | Motivo |
|---|---|
| Synthetic Monitoring (uptime checks) | Precisa de token SM gerado no Grafana UI (Testing & Synthetics → Config) |
| Cloudflare analytics alerts (5xx, ameaças) | Nenhum token existente tem `Zone Analytics: Read` — criar novo no dashboard CF |
| Alertas Sentry | Sentry tem webhook nativo, não requer Grafana |
| SOCKSTAT como alert rule Grafana | Pode ser feita igual ao CLOSE_WAIT — não foi priorizada |

---

## Como testar o sistema

```bash
# Testar webhook end-to-end (envia WhatsApp + cria issue Linear)
curl -X POST https://alertas.cadencia.ia.br/webhook \
  -H "X-Webhook-Secret: $WEBHOOK_SECRET" \  # carregar de /opt/grafana-webhook/.env na VPS Master, ou 1Password Hosts > "grafana-webhook .env VPS Master"
  -H "Content-Type: application/json" \
  -d '{"status":"firing","labels":{"alertname":"Teste","severity":"warning","ruleGroup":"vps-infra"},"annotations":{"description":"Teste manual"}}'

# Verificar métricas customizadas na VPS
cat /var/lib/node_exporter/textfile_collector/custom_metrics.prom

# Ver log do webhook
sudo journalctl -u grafana-webhook -f

# Ver status das alert rules
curl -s "https://felipeluissalgueiro.grafana.net/api/v1/provisioning/alert-rules" \
  -H "Authorization: Bearer $GRAFANA_SA_TOKEN" | python3 -m json.tool
# $GRAFANA_SA_TOKEN: 1Password Hosts > "Grafana - Service account token - ClaudeCode"
```

---

## Notas Relacionadas

- [[Infra/VPS Master]]
- [[Infra/Traefik]]
- [[Projetos/Migração VPS produção]]
