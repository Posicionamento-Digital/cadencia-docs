# Monitoring Stack — Time Infra

> Arquitetura da observabilidade da PD: Grafana Cloud + Alloy + Loki + webhook v2 + 7 alert rules ativas + **Uptime Kuma** (camada visual desde 2026-08-10). Documento constitutivo — define **como** a stack é estruturada. Inventário ao vivo de alert rules está em `../context/alert-rules.md` (refresh quando mudar).
>
> **Camada visual complementar (Epic DEV-1739+1740, ago/2026):**
> - [Uptime Kuma](./uptime-kuma.md) (`https://status.cadencia.ia.br`) — 18 monitores endpoint + alerta WhatsApp comercial.
> - [Beszel](./beszel.md) (`https://metrics.cadencia.ia.br`) — métricas host+container em 4 máquinas (Master/Dev/CAIXA1/Dell) + 16 alerts calibrados por perfil.
> - Grafana continua como investigação profunda + alerta automático background.

---

## Diagrama lógico

```
VPS Master  ─┬─► Alloy (agente leve) ─► Loki (logs Grafana Cloud)
             │                          └─► Prometheus remote_write (Grafana Cloud)
             │
             ├─► /opt/scripts/collect-custom-metrics.py (cron */1min)
             │       └─► /var/lib/node_exporter/textfile_collector/custom_metrics.prom
             │             └─► node_exporter ─► Alloy ─► Prometheus
             │
             └─► /opt/scripts/monitor-vps.sh (cron */5min)
                     └─► SOCKSTAT > 10k → WhatsApp Stevo direto (canal lateral, não passa Grafana)

Grafana Cloud ─► 7 Alert Rules
                     └─► Contact Point único: webhook v2
                             └─► /opt/grafana-webhook/main.py (systemd grafana-webhook.service, porta 9300)
                                     ├─► WhatsApp Stevo (notificação imediata Felipe — sempre)
                                     └─► Linear (issue label=auto-fix — só firing + sem dedup hit)

PDL-223 Fase 4 (futuro):
Linear (label=auto-fix) ─► runbook-executor.py ─► runbooks/ALLOWLIST.md check ─► <runbook>.sh
                                                          └─► escala WhatsApp (caso novo / não permitido)
```

---

## Componentes

### Grafana Cloud (`felipeluissalgueiro.grafana.net`)

- **Tier:** Cloud Free (suficiente pra volume PD atual)
- **Folder UID alert rules:** `cfn2d5qqfy41sa`
- **Grupos de alert rules:**
  - `vps-infra` — performance e capacidade (load, traefik RAM, CLOSE_WAIT, disco, RAM, Vercel deploy)
  - `vps-security` — eventos de segurança (SSH brute force, futuros CF analytics quando token permitir)
- **Pipeline obrigatório:** A (PromQL/Loki) → B (Reduce: last) → C (Math: $B > threshold). Não dá pra comparar time series direto no Math.

### Alloy (Grafana Alloy — agente unificado)

- Substitui Promtail + Grafana Agent + node_exporter scrapers (consolida em um binário)
- Lê `/var/lib/node_exporter/textfile_collector/*.prom` (métricas customizadas)
- Faz tail dos logs sistema (`/var/log/auth.log`, `/var/log/syslog`, `journalctl`)
- Envia tudo pra Grafana Cloud via remote_write + Loki push
- **Critical:** user `alloy` precisa permissão de leitura nos `.prom` (cron escreve como root → `chmod 0o644` no tmp antes do `os.rename`)

### Loki

- Recebe logs do Alloy (sistema + auth + journalctl)
- Usado em alert rule `SSH Brute Force`: `count_over_time({job="auth"} |= "Failed password" [5m]) > 10`

### Métricas customizadas (textfile_collector)

Script: `/opt/scripts/collect-custom-metrics.py` (cron `* * * * *`, user root).
Saída: `/var/lib/node_exporter/textfile_collector/custom_metrics.prom`.

| Métrica | Fonte | O que mede |
|---|---|---|
| `traefik_memory_bytes` | `docker stats coolify-proxy` | RAM container Traefik |
| `tcp_close_wait_total` | `ss -ant` | Conexões TCP em CLOSE_WAIT |
| `vercel_deploy_failed{project="..."}` | Vercel API v9 (16 projects) | 1 se último deploy falhou, 0 ok |

**Pegadinhas técnicas:**
- Escrita atômica: `tempfile.mkstemp` + `os.chmod(tmp, 0o644)` + `os.rename` (evita leitura parcial pelo Alloy)
- `VERCEL_TOKEN` hoje em crontab root — **vazamento conhecido**, vai pra `.env` em PDL-243

### Webhook v2 (`/opt/grafana-webhook/main.py`)

- Systemd: `grafana-webhook.service` (porta 9300)
- Endpoint: `https://alertas.cadencia.ia.br/webhook` (atrás do Coolify proxy + Cloudflare)
- Auth: header `X-Webhook-Secret`
- **Fluxo:**
  1. Valida secret
  2. Parseia payload (Alertmanager format ou simples — suporta ambos)
  3. Detecta squad via `labels.ruleGroup` → roteamento (`vps-infra → infra`, `vps-security → security`, etc)
  4. Envia WhatsApp Stevo (sempre — notificação imediata Felipe)
  5. Se `status="firing"`:
     - Calcula fingerprint (campo nativo ou MD5 de `alertname+labels`)
     - Checa cache `/opt/grafana-webhook/alert_cache.json` (TTL 30min)
     - Duplicata → skip Linear
     - Novo → cria issue Linear `[ALERTA][squad] nome` com label `auto-fix`

### Workers paralelos (canal lateral — não passa Grafana)

- `/opt/scripts/monitor-vps.sh` (cron `*/5min`, user master) — SOCKSTAT > 10k → WhatsApp Stevo direto. Pré-Grafana, mantido como redundância.

---

## 7 Alert Rules ativas

Inventário detalhado (rule UID, source PromQL/LogQL, threshold, severity): `../context/alert-rules.md`.

Resumo:

| Rule | Threshold | For | Severity | Categoria |
|---|---|---|---|---|
| VPS Load Average Alto | load > nCPUs | 5m | high | infra/load |
| Traefik RAM Alta | > 500MiB | 5m | high | infra/traefik |
| TCP CLOSE_WAIT Excessivo | > 1000 | 5m | medium | infra/tcp |
| Disco Raiz Baixo | < 15% | 10m | high | infra/disco |
| RAM Disponível Baixa | < 20% | 10m | medium | infra/ram |
| SSH Brute Force | > 10 fails em 5m | 0s | high | security |
| Vercel Deploy Falhado | >= 1 deploy falhado | 2m | medium | infra/vercel |

---

## Como adicionar nova alert rule

Via Provisioning API (token SA Grafana no 1P):

```bash
SA=$(op item get "Grafana - Service account token - ClaudeCode" --vault Hosts --fields credencial --reveal)
curl -X POST "https://felipeluissalgueiro.grafana.net/api/v1/provisioning/alert-rules" \
  -H "Authorization: Bearer $SA" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Template payload + exemplos Python/curl: nota Obsidian `Obsidian_Vaults_Empresa/Infra/Stack-Monitoramento-VPS-Master.md`.

**Checklist nova alert rule:**
1. Define metric source (Prometheus query ou Loki LogQL)
2. Define threshold + `for` (duração antes de disparar)
3. Define severity (`high` / `medium` / `low`)
4. Define grupo (`vps-infra` ou `vps-security` — novos grupos = novo doc)
5. Cria via Provisioning API
6. Testa fingerprint dedup (dispara duas vezes em < 30min, segunda deve ser silenciada)
7. Cria runbook correspondente em `runbooks/<categoria>/<rule>.sh` (se ação automatizada possível) e atualiza `runbook-overview.md`

---

## Pendências conhecidas

| Item | Motivo / unblock |
|---|---|
| Synthetic Monitoring (uptime checks externos) | Precisa token SM gerado no Grafana UI |
| Cloudflare analytics alerts (5xx, ameaças) | Token CF atual sem `Zone Analytics: Read` — precisa upgrade permissão |
| Alertas Sentry direto | Sentry tem webhook nativo, não passa Grafana |
| SOCKSTAT como alert rule Grafana | Pode duplicar CLOSE_WAIT — não priorizado |

---

## Vazamentos credencial mapeados (PDL-243)

| Item | Onde | Status |
|---|---|---|
| SA Grafana token | Obsidian `Obsidian_Vaults_Empresa/Infra/Stack-Monitoramento-VPS-Master.md` | Texto removido 24/05; **rotação pendente** |
| `VERCEL_TOKEN` | Crontab root VPS Master linha 1 | Pendente — mover pra `.env` + rotacionar |

---

## Refs

- `../context/alert-rules.md` — inventário ao vivo das 7 rules (threshold, UID, PromQL/Loki)
- Nota Obsidian `Obsidian_Vaults_Empresa/Infra/Stack-Monitoramento-VPS-Master.md` — doc técnica detalhada (criação API + payloads + troubleshoot)
- `docs/plans/fase-4-auto-fix-observabilidade.md` — runbook-executor consumindo issues `label=auto-fix` deste webhook
- `runbook-overview.md` — formato runbooks + códigos de saída
- `allowlist-policy.md` — quais containers/services podem ser restartados via runbook
- `security-principles.md` — VPS Master determinística (webhook v2 = script Python, não agente Claude)
- PDL-223 — Central de Observabilidade + Auto-correção com IA
- PDL-243 — auditoria credenciais
