# VPS Hostinger — PD Marketing Pipeline

## Acesso

**SSH (preferido):**
```bash
ssh -i ~/.ssh/hostinger_pd root@72.60.4.71
```

**Senha root (fallback):** `PD-Pipeline@2026`

**Via Python/paramiko (automação):**
```python
import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("72.60.4.71", username="root", password="PD-Pipeline@2026",
               timeout=30, allow_agent=False, look_for_keys=False)
```

## Chaves e IDs

| Item | Valor |
|---|---|
| IP | `72.60.4.71` |
| VPS ID | `1596526` |
| Hostname | `srv1596526.hstgr.cloud` |
| SSH Key ID | `492691` (pd-marketing-pipeline) |
| Chave local | `~/.ssh/hostinger_pd` |
| Hostinger API Token | ver `.env` |

## Ambiente na VPS

| Item | Detalhe |
|---|---|
| OS | Ubuntu 24.04 |
| Python | `/usr/bin/python3` (3.12) |
| Node.js | v20.20.2 |
| Claude Code CLI | 2.1.112 (autenticado com conta Max do Felipe) |
| Repo | `/root/pd-marketing` |
| `.env.remote` | `/root/pd-marketing/.env.remote` |

## Crons ativos

```
0 14 * * *   → disparo-seinfeld.py     → 14h UTC = 11h BRT, todos os dias
0 15 * * 5   → disparo-newsletter.py  → 15h UTC = 12h BRT, toda sexta
```

Para ver/editar: `ssh -i ~/.ssh/hostinger_pd root@72.60.4.71 "crontab -l"`

## Gerenciar via Hostinger API

**Base URL:** `https://developers.hostinger.com/api/vps/v1/`
**Token:** ver `.env` → `HOSTINGER_API_TOKEN`

```bash
# Listar VPS
curl -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  https://developers.hostinger.com/api/vps/v1/virtual-machines

# Resetar senha root
curl -X PUT -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  https://developers.hostinger.com/api/vps/v1/virtual-machines/1596526/root-password \
  -d '{"password": "nova-senha"}'

# Restart VPS
curl -X POST -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  https://developers.hostinger.com/api/vps/v1/virtual-machines/1596526/restart
```

## Guardrail absoluto

**Nunca deletar, reinstalar ou sobrescrever dados na VPS sem confirmação explícita do Felipe.**
Operações destrutivas via API (`/recreate`, `/reinstall`) requerem confirmação textual antes de executar.

## Atualizar o repo na VPS

```bash
ssh -i ~/.ssh/hostinger_pd root@72.60.4.71 "cd /root/pd-marketing && git pull origin master"
```

## Ver logs

```bash
# Seinfeld
ssh -i ~/.ssh/hostinger_pd root@72.60.4.71 "tail -50 /root/pd-marketing/logs/cron-seinfeld.log"

# Newsletter
ssh -i ~/.ssh/hostinger_pd root@72.60.4.71 "tail -50 /root/pd-marketing/logs/cron-newsletter.log"
```
