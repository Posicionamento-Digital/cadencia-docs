---
date: 2026-06-24
tags: [doc, infra, vps, deploy, central-cs]
moc: "[[MOC-Projetos]]"
status: ativo
type: source
entities: ["[[Cadencia]]", "[[comercial]]"]
---
# Infra & Deploy (VPS Master)

> Runbook resumido. Fonte canônica: `pd-framework/times/cs/context/infra-deploy-onboarding.md`.

## Topologia

- VPS: `master@72.60.4.71` (Hostinger KVM2 4vCPU 8GB BR)
- `/opt/onboarding-webhooks/` — repo clone do receiver
- `/opt/pd-framework/` — clone pd-framework (consumer)
- `/etc/onboarding/op.env` — env do container (não commitado)
- `/etc/systemd/system/onboarding-consumer.service`
- Traefik gerencia DNS + SSL (subdomínio `.cadencia.ia.br`)

## Deploy receiver

```bash
ssh master@72.60.4.71
cd /opt/onboarding-webhooks && git pull
docker build --no-cache -t onboarding-webhooks .   # F1: --no-cache obrigatório
docker rm -f onboarding-webhooks
docker run -d --name onboarding-webhooks --restart=always \
  --env-file /etc/onboarding/op.env \
  -v /opt/onboarding-webhooks/queue:/app/queue \
  -p 9400:9400 onboarding-webhooks
curl localhost:9400/health
```

## Deploy consumer

```bash
cd /opt/pd-framework && git pull
sudo cp times/cs/workers/onboarding-consumer/onboarding-consumer.service /etc/systemd/system/
sudo systemctl daemon-reload && systemctl enable --now onboarding-consumer
journalctl -u onboarding-consumer -f
```

## Env vars (resumo)

| Receiver (`/etc/onboarding/op.env`) | Consumer (`.env` no diretório do worker) |
|---|---|
| `WEBHOOK_SECRET` | `ONBOARDING_QUEUE_DIR=/opt/onboarding-webhooks/queue/onboarding` |
| `CALCOM_WEBHOOK_SECRET` | `ONBOARDING_TENANT_ID=6bb2c1ba-...` |
| `EVO_URL=https://evo.cadencia.ia.br` | `ONBOARDING_APPLY=1` |
| `EVO_TOKEN_DEFAULT` | `ONBOARDING_ALERTA_PARA=5511914912127` |
| `EVO_DEFAULT_NUMBER=5511914912127` | `ONBOARDING_SLACK_CANAL=rotina` |
| `LINEAR_TOKEN` | `OP_SERVICE_ACCOUNT_TOKEN` |
| `ONBOARDING_QUEUE_DIR=/app/queue/onboarding` | |
| `ASAAS_DEDUP_DIR=/app/queue/asaas_seen` | |

> Mesmo path de fila dos dois lados (volume montado).

## Credenciais (1P)

- Evo pessoal/comercial → vault `E-mails`, items `EVO - API  - Num pessoal` (2 espaços) e `EVO - API - Num comercial`, campo `password`.
- Cal.com API + webhook secret → vault `E-mails`, item `Cal.com - API - ClaudeCode`.
- Linear API → vault `Serviços & Tools`.

## Webhooks externos

- Tally: `POST /tally` + header `X-Webhook-Secret`.
- Cal.com: `POST /calcom` + HMAC-SHA256 do corpo (`X-Cal-Signature-256`).
- Asaas: `POST /asaas` + header `X-Webhook-Secret`, eventos PAYMENT_RECEIVED/CONFIRMED.

## Don'ts

- Não `docker build` sem `--no-cache`.
- Não rodar agente Claude tool-use na Master.
- Não mergear em produção sem autorização explícita do Felipe (DEV-WORKFLOW §12.0b).
- Não ligar APPLY=1 antes do dry_run real.

## Relacionadas

- [[00-Visao-Geral]] · [[02-Receiver]] · [[03-Consumer]]
